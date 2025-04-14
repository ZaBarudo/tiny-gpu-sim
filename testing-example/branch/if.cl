__kernel void if_kernel(__global int* a, __global int* result) {
    int i = get_global_id(0);
    if(a[i] > 0) result[i] = 1;
}
