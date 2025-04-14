__kernel void div_imm(__global int* a, int imm, __global int* result) {
    int i = get_global_id(0);
    result[i] = a[i] / imm;
}
