### Pod管理

#### Pod介绍

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_introduce.md

#### Pod管理-创建/查询/更新/删除

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_create.md

#### Pod管理-资源限制

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_limit.md

#### Pod管理-调度约束

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_schedule.md

#### Pod管理-重启策略

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_restart.md

#### Pod管理-健康检查

https://github.com/hdpingshao/ops/blob/master/kubernetes/content/pod_check.md

#### Pod管理-问题定位

###### 状态描述

|值|描述|
|---|---|
|Pending|Pod创建已经提交到Kubernetes。但是，因为某种原因而不能顺利创建。例如下载镜像慢，调度不成功。|
|Running|Pod已经绑定到一个节点，并且已经创建了所有容器。至少有一个容器正在运行中，或正在启动或重新启动|
|Succeeded|Pod中的所有容器都已经成功终止，不会重新启动。|
|Failed|Pod的所有容器均已终止，且至少有一个容器已在故障中终止。也就是说，容器要么以非零状态退出，要么被系统终止|
|Unknown|由于某种原因apiserver无法获得Pod的状态，通常时由于Master与Pod所在主机kubelet通信时出错|
|Completed|容器内的任务已经执行完成并退出|

    kubectl describe TYPE NAME_PREFIX
    kubectl logs nginx-xxx
    kubectl exec -it nginx-xxx bash