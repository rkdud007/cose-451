# Report

2020170365 gayeong park

## Location of the Vulnerability

The vulnerability was located in the Rust standard library, specifically within the `alloc` crate. The affected code is found in two files:

1. **File:** `rust/library/alloc/src/vec/source_iter_marker.rs`

   - **Lines:** 71 to 72

   ```rust
   // drop any remaining values at the tail of the source
   src.drop_remaining();
   ```

2. **File:** `rust/library/alloc/src/vec/into_iter.rs`
   - **Lines**: 88 to 93
   ```rust
   pub(super) fn drop_remaining(&mut self) {
    unsafe {
        ptr::drop_in_place(self.as_mut_slice());
    }
    self.ptr = self.end;
   }
   ```

## Triggering the Vulnerability

The vulnerability is triggered when `drop_remaining()` is called. This function attempts to drop the remaining elements in a vector by calling `ptr::drop_in_place` on a slice derived from a mutable reference. Here’s a detailed explanation:

1. Function Call: `drop_remaining()` is invoked.
2. Unsafe Operation: Inside `drop_remaining()`, the `ptr::drop_in_place` function is called on the slice obtained from `self.as_mut_slice()`.
3. Pointer Update: After dropping the elements, the pointer self.ptr is set to self.end.

This sequence can cause elements to be dropped twice in certain circumstances. Specifically, if a panic occurs during the drop operation (as in the provided proof of concept), Rust’s panic unwinding mechanism may attempt to drop the elements again, leading to a double free error. This is dangerous because it can cause undefined behavior, such as memory corruption or crashes.

## Proof of Concept (PoC)

The provided PoC demonstrates how this vulnerability can be exploited:

```rust
#![forbid(unsafe_code)]

use std::iter::FromIterator;

#[derive(Debug)]
enum MyEnum {
    DroppedTwice(Box<i32>),
    PanicOnDrop,
}

impl Drop for MyEnum {
    fn drop(&mut self) {
        match self {
            MyEnum::DroppedTwice(_) => println!("Dropping!"),
            MyEnum::PanicOnDrop => {
                if !std::thread::panicking() {
                    panic!();
                }
            }
        }
    }
}

fn main() {
    let v = vec![MyEnum::DroppedTwice(Box::new(123)), MyEnum::PanicOnDrop];
    Vec::from_iter(v.into_iter().take(0));
}

```

### Output

```sh
Dropping!
thread 'main' panicked at 'explicit panic', src/main.rs:17:21
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
Dropping!
free(): double free detected in tcache 2
```

n the PoC, the vector v contains elements that trigger a panic during the drop operation. The PanicOnDrop variant causes a panic unless the thread is already panicking. This leads to drop_remaining() being called again due to panic unwinding, causing the DroppedTwice variant to be dropped twice, as shown by the "Dropping!" messages and the resulting double free error.

## Patch for the Vulnerability

The vulnerability was patched by modifying the way elements are dropped to prevent multiple drops under panic conditions. The corrected approach consolidates the functionality of forgetting the allocation and dropping the remaining elements into a single operation. Here’s how it was patched:

````rust
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
````

In this patch, the `forget_allocation` and `drop_remaining` functions are combined into one function, `forget_allocation_drop_remaining()`. This new function ensures that the backing allocation is relinquished by resetting the vector's internal state (capacity and pointers) before dropping the remaining elements. By overwriting the internal state first, it prevents the possibility of the elements being dropped multiple times under panic conditions.

## Confirmation that the vulnerablilty is no longer triggered

Running the same PoC with the patched version did not result in a double free error. The "Dropping!" message appeared only once for each drop operation, and the program handled the panic without crashing or causing undefined behavior :

```sh
thread 'main' panicked at src/main.rs:17:21:
explicit panic
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
Standard Output
Dropping!
```

### Reference

Most of the work was highly referenced and learned from
[issue#83618](https://github.com/rust-lang/rust/issues/83618) and [patch commit](https://github.com/rust-lang/rust/commit/542f441d445026d0996eebee9ddddee98f5dc3e5).
