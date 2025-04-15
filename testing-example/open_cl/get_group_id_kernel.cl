__kernel void get_group_id_kernel(__global int* result) {
    result[get_global_id(0)] = get_group_id(0);
}