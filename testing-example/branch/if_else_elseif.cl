__kernel void if_else_elseif(__global int* a, __global int* result) {
    int i = get_global_id(0);
    if(a[i] > 10) result[i] = 2;
    else if(a[i] > 0) result[i] = 1;
    else result[i] = 0;
}