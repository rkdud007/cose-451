````rust
// =============================================================================
// The code base below is from `library/alloc/src/vec/into_iter.rs`
// =============================================================================

/// Drops remaining elements and relinquishes the backing allocation.
///
/// This is roughly equivalent to the following, but more efficient
///
/// ```
/// # let mut into_iter = Vec::<u8>::with_capacity(10).into_iter();
/// (&mut into_iter).for_each(core::mem::drop);
/// unsafe { core::ptr::write(&mut into_iter, Vec::new().into_iter()); }
/// ```
pub(super) fn forget_allocation_drop_remaining(&mut self) {
    let remaining = self.as_raw_mut_slice();

    // overwrite the individual fields instead of creating a new
    // struct and then overwriting &mut self.
    // this creates less assembly
    self.cap = 0;
    self.buf = unsafe { NonNull::new_unchecked(RawVec::NEW.ptr()) };
    self.ptr = self.buf.as_ptr();
    self.end = self.buf.as_ptr();

    unsafe {
        ptr::drop_in_place(remaining);
    }
}

// =============================================================================
// The code base below is from `library/alloc/src/vec/source_iter_marker.rs`
// =============================================================================

// drop any remaining values at the tail of the source
// but prevent drop of the allocation itself once IntoIter goes out of scope
// if the drop panics then we also leak any elements collected into dst_buf
src.forget_allocation_drop_remaining();
````
