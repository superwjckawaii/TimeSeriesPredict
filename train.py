import CNN
import numpy as np
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from data_process import TimeSeriesDataset, data_process

if "__main__" == __name__:

    train_data, valid_data, _ = data_process()

    # ########## 测试（不加时间数据）
    train_ground_truth = np.array([train_data['active_index'], train_data['consume_index']])
    train_ground_truth = list(zip(*train_ground_truth))

    valid_ground_truth = np.array([valid_data['active_index'], valid_data['consume_index']])
    valid_ground_truth = list(zip(*valid_ground_truth))

    # 示例数据
    train_data = np.array(train_data)
    valid_data = np.array(valid_data)

    X = train_data[:, 2:-2].astype(float)
    y = train_data[:, -2:].astype(float)

    valid_X = valid_data[:, 2:-2].astype(float)
    valid_y = valid_data[:, -2:].astype(float)

    # # 转换为PyTorch张量
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32)

    valid_X = torch.tensor(valid_X, dtype=torch.float32)
    valid_y = torch.tensor(valid_y, dtype=torch.float32)
    #
    # 创建数据加载器
    batch_size = 30
    train_dataset = TimeSeriesDataset(X, y)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size)

    valid_dataset = TimeSeriesDataset(valid_X, valid_y)
    valid_dataloader = DataLoader(valid_dataset, batch_size=batch_size)

    # ########## 测试（不加时间数据）

    # 参数设置
    input_size = 35
    output_size = 2
    num_channels = [68] * 4
    kernel_size = 2
    dropout = 0.2
    model = CNN.TCN(input_size, output_size, num_channels, kernel_size, dropout)

    # 损失函数
    criterion = nn.MSELoss()

    # 优化器
    lr = 0.001
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_loss = 999


    # 训练
    epochs = 20
    for epoch in range(epochs):
        total_loss = 0
        for i, (X, y) in enumerate(train_dataloader):
            y_pred = model(X.unsqueeze(2))
            loss = criterion(y_pred, y)
            loss = torch.sqrt(loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            # 每20个batch打印一次损失
            if (i + 1) % 20 == 0:
                print('Epoch {}, Batch {}/{}, Loss {}'.format(epoch + 1, i + 1, len(train_dataloader), loss.item()))
        # 验证(不进行参数更新）
        for j, (X, y) in enumerate(valid_dataloader):
            y_pred = model(X.unsqueeze(2))
            loss = criterion(y_pred, y)
            loss = torch.sqrt(loss)
            total_loss += loss.item()

        if total_loss / len(valid_dataloader) < best_loss:
            best_loss = total_loss / len(valid_dataloader)

        # 每个epoch打印一次平均损失
        print('Epoch {}, Valid_Loss {}'.format(epoch + 1, total_loss / len(valid_dataloader)))
        print(f'best_loss{best_loss}')

