; ModuleID = './testing-example/branch/if_else.cl'
source_filename = "./testing-example/branch/if_else.cl"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "tinygpu"

; Function Attrs: convergent noinline norecurse nounwind optnone
define dso_local spir_kernel void @if_else(ptr noundef align 4 %a, ptr noundef align 4 %b, ptr noundef align 4 %result) #0 !kernel_arg_addr_space !4 !kernel_arg_access_qual !5 !kernel_arg_type !6 !kernel_arg_base_type !6 !kernel_arg_type_qual !7 {
entry:
  %a.addr = alloca ptr, align 4
  %b.addr = alloca ptr, align 4
  %result.addr = alloca ptr, align 4
  %i = alloca i32, align 4
  store ptr %a, ptr %a.addr, align 4
  store ptr %b, ptr %b.addr, align 4
  store ptr %result, ptr %result.addr, align 4
  %call = call i32 @_Z13get_global_idj(i32 noundef 0) #2
  store i32 %call, ptr %i, align 4
  %0 = load ptr, ptr %a.addr, align 4
  %1 = load i32, ptr %i, align 4
  %arrayidx = getelementptr inbounds i32, ptr %0, i32 %1
  %2 = load i32, ptr %arrayidx, align 4
  %cmp = icmp sgt i32 %2, 10
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %3 = load ptr, ptr %result.addr, align 4
  %4 = load i32, ptr %i, align 4
  %arrayidx1 = getelementptr inbounds i32, ptr %3, i32 %4
  store i32 1, ptr %arrayidx1, align 4
  br label %if.end

if.else:                                          ; preds = %entry
  %5 = load ptr, ptr %result.addr, align 4
  %6 = load i32, ptr %i, align 4
  %arrayidx2 = getelementptr inbounds i32, ptr %5, i32 %6
  store i32 2, ptr %arrayidx2, align 4
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  ret void
}

; Function Attrs: convergent nounwind willreturn memory(none)
declare dso_local i32 @_Z13get_global_idj(i32 noundef) #1

attributes #0 = { convergent noinline norecurse nounwind optnone "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "uniform-work-group-size"="true" }
attributes #1 = { convergent nounwind willreturn memory(none) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" }
attributes #2 = { convergent nounwind willreturn memory(none) }

!llvm.module.flags = !{!0, !1}
!opencl.ocl.version = !{!2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"frame-pointer", i32 2}
!2 = !{i32 1, i32 2}
!3 = !{!"clang version 20.0.0git (https://github.com/ZaBarudo/tiny-gpu-lang-backend.git 5bbe75a55c5c353b4162b2189d15853f35272982)"}
!4 = !{i32 1, i32 1, i32 1}
!5 = !{!"none", !"none", !"none"}
!6 = !{!"int*", !"int*", !"int*"}
!7 = !{!"", !"", !""}
