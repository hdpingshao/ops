### 常用操作

#### 1、创建

    kubectl run nginx --replicas=3 --labels="app=test" --image=nginx:1.10 --port=80
    
#### 2、查看

    kubectl get deploy
    kubectl get pods --show-labels
    kubectl get pods -l app=test
    kubectl get pods -o wide

#### 3、发布

    kubectl expose deployment nginx --port=88 --type=NodePort --target-port=80 --name=nginx-service
    kubectl describe service nginx-service
    
#### 4、故障排查

    kubectl describe TYPE NAME_PREFIX
    kubectl logs nginx-xxx
    kubectl exec -it nginx-xxx bash
    
#### 5、更新

    kubectl set image deployment/nginx nginx=nginx:1.11
    kubectl set image deployment/nginx nginx=nginx:1.12 --record=true
    kubectl edit deployment/nginx
    
#### 6、资源发布管理
    
    kubectl rollout status deployment/nginx
    kubectl rollout history deployment/nginx
    kubectl rollout history deployment/nginx --revision=3
    
    kubectl scale deployment nginx --replicas=10
    
#### 7、回滚

    kubectl rollout undo deployment/nginx-deployment
    kubectl rollout undo deployment/nginx-deployment --to-revision=3
   
#### 8、删除

    kubectl delete deploy/nginx
    kubectl delete svc/nginx-service
