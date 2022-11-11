import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def train_model(net,train_dl,test_dl,scenario,
                       lr0=0.001,a=0.001,b=0.75,momentum=0.9,weight_decay=0.0001,num_epoch=10,batch_size=64,
                       logger=None,device=torch.device('cpu'),step0=0):
    net.to(device);
    net.train();
    
    step=0;
    bs = batch_size
    N = len(train_dl.dataset)
    myiterations = (N//bs+1)*num_epoch
    lr_scheduler=exp_lr_decay(lr0,a,b);

    net_param = [];
    for name,param in net.named_parameters():
        if name[:6] == 'linear':
            continue;
        net_param.append(param);
    
    optimizer = torch.optim.SGD([
        {'params': net_param},
        {'params': net.linear.parameters()}], lr=lr0, momentum=momentum, weight_decay=weight_decay);
    loss_func = nn.CrossEntropyLoss(reduction='mean',label_smoothing=0.1);
    
    epoch_loss = []; epoch_acc =[];
    for epoch in range(num_epoch):
        print(f'----- EPOCH {epoch+1} -----')   
        batch_loss=[];batch_acc=[];
        for batch_idx, (images, labels) in enumerate(train_dl):
            images, labels = images.to(device), labels.type(torch.LongTensor).to(device)
            
            net.zero_grad();
            output = net(images);
            loss = loss_func(output, labels)
            pred = output.data.max(1, keepdim=True)[1]  # get the index of the max log-probability
            acc = 100*pred.eq(labels.data.view_as(pred)).long().sum()/batch_size;
            loss.backward()
            
            lr = lr_scheduler(step);
            optimizer.param_groups[0]['lr'] = lr;
            optimizer.param_groups[1]['lr'] = 10*lr;
            optimizer.step()
            batch_loss.append(loss.item())
            batch_acc.append(acc)
            
            # print(f'lr: {lr} \ttrain_loss: {loss.item()}')
            if logger:
                logger.add_scalars({"loss":loss.item()},f"train_loss/{scenario}",step=step+step0);
                logger.add_scalars({"acc":acc.item()},f"train_acc/{scenario}",step=step+step0);
            
            if step+1 in [int(0.10*myiterations), int(0.2*myiterations), int(0.5*myiterations), int(0.8*myiterations), int(0.99*myiterations)]:
                net.eval();
                test_loss,test_acc = test_model(net,test_dl,device=device);
                net.train();
                print(f'lr: {lr} \tAvgTrainLoss: {sum(batch_loss)/len(batch_loss)} \tAvgTrainAcc: {sum(batch_acc)/len(batch_acc)} \tTestLoss: {test_loss} \tTestAcc: {test_acc}')
                if logger:
                    logger.add_weight_dist(net.state_dict(),f"{scenario}",step=step+step0);
                    logger.add_scalars({"loss":test_loss.item()},f"test_loss/{scenario}",step=step+step0);
                    logger.add_scalars({"accuracy":test_acc.item()},f"test_accuracy/{scenario}",step=step+step0);
            step+=1
        
        epoch_loss.append(sum(batch_loss)/len(batch_loss))
        epoch_acc.append(sum(batch_acc)/len(batch_acc))
        print(f'AvgTrainLoss: {sum(batch_loss)/len(batch_loss)} \tAvgTrainAcc: {sum(batch_acc)/len(batch_acc)}')
    
    test_loss,test_acc = test_model(net,test_dl,device=device);
    print(f'Final TestLoss: {test_loss} \tTestAcc: {test_acc}')
    if logger:
        logger.add_weight_dist(net.state_dict(),f"{scenario}",step=step+step0);
        logger.add_scalars({"loss":test_loss.item()},f"test_loss/{scenario}",step=step+step0);
        logger.add_scalars({"accuracy":test_acc.item()},f"test_accuracy/{scenario}",step=step+step0);
        
    return net.state_dict(), epoch_loss[-1], epoch_acc[-1], test_loss,test_acc, step+step0


def exp_lr_decay(lr0,a,b):
    def exp_lr_fn(i):
        return lr0*((1+a*i)**(-1*b));
    return exp_lr_fn;

def test_model(net,test_dl,device=torch.device('cpu')):
    net.to(device)
    net.eval()
    test_loss = torch.tensor(0.0,device=device);
    correct = torch.tensor(0.0,device=device);
    criterion = nn.CrossEntropyLoss(reduction="sum").to(device)
    with torch.no_grad():
        for i,(data,target) in enumerate(test_dl):
            data, target = data.to(device), target.type(torch.LongTensor).to(device)
            
            output = net(data)
            test_loss += criterion(output, target).item()  # sum up batch loss
            pred = output.data.max(1, keepdim=True)[1]  # get the index of the max log-probability
            correct += pred.eq(target.data.view_as(pred)).long().sum()
    test_loss /= len(test_dl.dataset)
    accuracy = 100. * correct / len(test_dl.dataset)
    return test_loss.detach().cpu().numpy(), accuracy.detach().cpu().numpy()