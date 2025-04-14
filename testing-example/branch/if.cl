__kernel void if_kernel(__global int* a, __global int* b, __global int* result) {
    int i = get_global_id(0);
    if(a[i] > 10) result[i] = 1;
}
