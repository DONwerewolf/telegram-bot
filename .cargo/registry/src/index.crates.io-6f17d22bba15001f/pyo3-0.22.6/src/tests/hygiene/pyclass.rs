#[crate::pyclass]
#[pyo3(crate = "crate")]
#[derive(::std::clone::Clone)]
pub struct Foo;

#[crate::pyclass]
#[pyo3(crate = "crate")]
pub struct Foo2;

#[cfg_attr(any(Py_3_9, not(Py_LIMITED_API)), crate::pyclass(
    name = "ActuallyBar",
    freelist = 8,
    unsendable,
    subclass,
    extends = crate::types::PyAny,
    module = "Spam",
    weakref,
    dict
))]
#[cfg_attr(not(any(Py_3_9, not(Py_LIMITED_API))), crate::pyclass(
    name = "ActuallyBar",
    freelist = 8,
    unsendable,
    subclass,
    extends = crate::types::PyAny,
    module = "Spam"
))]
#[pyo3(crate = "crate")]
pub struct Bar {
    #[pyo3(get, set)]
    a: u8,
    #[pyo3(get, set)]
    b: Foo,
    #[pyo3(set)]
    c: ::std::option::Option<crate::Py<Foo2>>,
}

#[crate::pyclass(eq, eq_int)]
#[pyo3(crate = "crate")]
#[derive(PartialEq)]
pub enum Enum {
    Var0,
}

#[crate::pyclass]
#[pyo3(crate = "crate")]
pub struct Foo3 {
    #[pyo3(get, set)]
    #[cfg(any())]
    field: i32,

    #[pyo3(get, set)]
    #[cfg(not(any()))]
    field: u32,
}

#[crate::pyclass]
#[pyo3(crate = "crate")]
pub struct Foo4 {
    #[pyo3(get, set)]
    #[cfg(any())]
    #[cfg(not(any()))]
    field: i32,

    #[pyo3(get, set)]
    #[cfg(not(any()))]
    field: u32,
}

#[crate::pyclass(eq, ord)]
#[pyo3(crate = "crate")]
#[derive(PartialEq, PartialOrd)]
pub struct PointEqOrd {
    x: u32,
    y: u32,
    z: u32,
}

#[crate::pyclass(eq, ord)]
#[pyo3(crate = "crate")]
#[derive(PartialEq, PartialOrd)]
pub enum ComplexEnumEqOrd {
    Variant1 { a: u32, b: u32 },
    Variant2 { c: u32 },
}

#[crate::pyclass(eq, ord)]
#[pyo3(crate = "crate")]
#[derive(PartialEq, PartialOrd)]
pub enum TupleEnumEqOrd {
    Variant1(u32, u32),
    Variant2(u32),
}
