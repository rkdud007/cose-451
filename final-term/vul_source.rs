// =============================================================================
// The code base below is from `library/alloc/src/vec/into_iter.rs`
// =============================================================================

pub(super) fn drop_remaining(&mut self) {
    unsafe {
        ptr::drop_in_place(self.as_mut_slice());
    }
    self.ptr = self.end;
}

/// Relinquishes the backing allocation, equivalent to
/// `ptr::write(&mut self, Vec::new().into_iter())`
pub(super) fn forget_allocation(&mut self) {
    self.cap = 0;
    self.buf = unsafe { NonNull::new_unchecked(RawVec::NEW.ptr()) };
    self.ptr = self.buf.as_ptr();
    self.end = self.buf.as_ptr();
}

// =============================================================================
// The code base below is from `library/alloc/src/vec/source_iter_marker.rs`
// =============================================================================

// The std-internal SourceIter/InPlaceIterable traits are only implemented by chains of
// Adapter<Adapter<Adapter<IntoIter>>> (all owned by core/std). Additional bounds
// on the adapter implementations (beyond `impl<I: Trait> Trait for Adapter<I>`) only depend on other
// traits already marked as specialization traits (Copy, TrustedRandomAccess, FusedIterator).
// I.e. the marker does not depend on lifetimes of user-supplied types. Modulo the Copy hole, which
// several other specializations already depend on.
impl<T> SourceIterMarker for T where T: SourceIter<Source: AsIntoIter> + InPlaceIterable {}
impl<T, I> SpecFromIter<T, I> for Vec<T>
where
    I: Iterator<Item = T> + SourceIterMarker,
{
    default fn from_iter(mut iterator: I) -> Self {
        // Additional requirements which cannot expressed via trait bounds. We rely on const eval
        // instead:
        // a) no ZSTs as there would be no allocation to reuse and pointer arithmetic would panic
        // b) size match as required by Alloc contract
        // c) alignments match as required by Alloc contract
        if mem::size_of::<T>() == 0
            || mem::size_of::<T>()
                != mem::size_of::<<<I as SourceIter>::Source as AsIntoIter>::Item>()
            || mem::align_of::<T>()
                != mem::align_of::<<<I as SourceIter>::Source as AsIntoIter>::Item>()
        {
            // fallback to more generic implementations
            return SpecFromIterNested::from_iter(iterator);
        }
        let (src_buf, src_ptr, dst_buf, dst_end, cap) = unsafe {
            let inner = iterator.as_inner().as_into_iter();
            (
                inner.buf.as_ptr(),
                inner.ptr,
                inner.buf.as_ptr() as *mut T,
                inner.end as *const T,
                inner.cap,
            )
        };
        let len = SpecInPlaceCollect::collect_in_place(&mut iterator, dst_buf, dst_end);
        let src = unsafe { iterator.as_inner().as_into_iter() };
        // check if SourceIter contract was upheld
        // caveat: if they weren't we may not even make it to this point
        debug_assert_eq!(src_buf, src.buf.as_ptr());
        // check InPlaceIterable contract. This is only possible if the iterator advanced the
        // source pointer at all. If it uses unchecked access via TrustedRandomAccess
        // then the source pointer will stay in its initial position and we can't use it as reference
        if src.ptr != src_ptr {
            debug_assert!(
                unsafe { dst_buf.add(len) as *const _ } <= src.ptr,
                "InPlaceIterable contract violation, write pointer advanced beyond read pointer"
            );
        }

        // drop any remaining values at the tail of the source
        src.drop_remaining();
        // but prevent drop of the allocation itself once IntoIter goes out of scope
        src.forget_allocation();

        let vec = unsafe { Vec::from_raw_parts(dst_buf, len, cap) };

        vec
    }
}
