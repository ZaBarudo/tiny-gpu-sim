__kernel void div_imm(__global float* a, float imm, __global float* result) {
    int i = get_global_id(0);
    result[i] = a[i] / imm;
}
