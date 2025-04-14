__kernel void get_global_id_kernel(__global int* result) {
    result[get_global_id(0)] = get_global_id(0);
}