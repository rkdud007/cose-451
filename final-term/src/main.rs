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
