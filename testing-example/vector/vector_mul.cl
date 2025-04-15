__kernel void vector_mul(__global int* a, __global int* b, __global int* c) {
    int i = get_global_id(0);
    c[i] = a[i] * b[i];
}