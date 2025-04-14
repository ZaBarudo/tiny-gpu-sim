__kernel void get_local_id_kernel(__global int* result) {
    result[get_global_id(0)] = get_local_id(0);
}
