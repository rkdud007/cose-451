use std::ptr;

impl Drop for MyStruct {
    fn drop(&mut self) {
        println!("Dropping MyStruct");
    }
}
struct MyStruct;

fn main() {
    let _my_struct = MyStruct;
    panic!("Oh no!")
}
