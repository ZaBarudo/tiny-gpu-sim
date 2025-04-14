__kernel void vector_add(__global float4* a, __global float4* b, __global float4* c) {
    int i = get_global_id(0);
    c[i] = a[i] + b[i];
}
