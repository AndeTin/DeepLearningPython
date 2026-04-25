import json

with open('digits_classification.new.ipynb', 'r') as f:
    nb = json.load(f)

# Find the code cell
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and len(cell['source']) > 0 and 'import torch\n' in cell['source']:
        # We found the source array. We will completely replace it.
        source = "".join(cell['source'])
        
        # We need to add TensorBoard
        new_source = """# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import random
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

# ===== choose dataset =====
# dataset：'MNIST', 'FashionMNIST', 'KMNIST'
dataset_name = 'FashionMNIST'

# ===== convolution kernel =====
custom_kernel = torch.zeros((32, 1, 3, 3))
custom_kernels = torch.stack([
    torch.tensor([[0, 1, 0],
                  [0, 1, 0],
                  [0, 1, 0]], dtype=torch.float32),
    torch.tensor([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]], dtype=torch.float32),
    torch.tensor([[0, 1, 0],
                  [1, 1, 1],
                  [0, 1, 0]], dtype=torch.float32)
]).unsqueeze(1)

# ===== CNN model =====
class CustomCNN(nn.Module):
    def __init__(self):
        super(CustomCNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=3, kernel_size=3, padding=1, bias=False)
        self.conv1.weight = nn.Parameter(custom_kernels, requires_grad=False)
        self.conv2 = nn.Conv2d(3, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 14 * 14, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 32 * 14 * 14)
        x = torch.relu(self.fc1(x))
        return x

# ===== load dataset =====
def load_dataset(name):
    transform = transforms.Compose([
        transforms.Grayscale(),  # Convert colors to grayscale
        transforms.ToTensor(),
    ])
    if name == 'MNIST':
        dataset = torchvision.datasets.MNIST
    elif name == 'FashionMNIST':
        dataset = torchvision.datasets.FashionMNIST
    elif name == 'KMNIST':
        dataset = torchvision.datasets.KMNIST
    else:
        raise ValueError("dataset loading error！")

    train_data = dataset(root='./data', train=True, transform=transform, download=True)
    test_data = dataset(root='./data', train=False, transform=transform, download=True)

    return train_data, test_data

# ===== train_and_test =====
def train_and_test():
    train_dataset, test_dataset = load_dataset(dataset_name)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CustomCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Initialize TensorBoard SummaryWriter
    writer = SummaryWriter('runs/fashion_mnist_experiment')

    # Log Graph and Images using the first batch
    dataiter = iter(train_loader)
    images, labels = next(dataiter)
    images_device = images.to(device)
    
    # Write graph
    writer.add_graph(model, images_device)
    
    # Write a batch of images
    img_grid = torchvision.utils.make_grid(images)
    writer.add_image('FashionMNIST_Images', img_grid)

    global_step = 0
    for epoch in range(3):
        model.train()
        running_loss = 0.0
        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
            # Log scalars (Loss)
            if i % 100 == 99:
                writer.add_scalar('Training Loss', running_loss / 100, global_step)
                running_loss = 0.0
            
            global_step += 1
            
        # Log Distributions and Histograms of weights after each epoch
        for name, weight in model.named_parameters():
            writer.add_histogram(f'Weights/{name}', weight, epoch)
            if weight.grad is not None:
                writer.add_histogram(f'Gradients/{name}', weight.grad, epoch)

        print(f"Epoch {epoch+1} complete.")

    # accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    accuracy = 100 * correct / total
    print(f"accuracy: {accuracy:.2f}%")
    
    # Log the final accuracy as a scalar
    writer.add_scalar('Test Accuracy', accuracy, global_step)
    
    # Close the writer
    writer.close()

# ===== main function =====
def set_seed(seed=100):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# ===== main function =====
if __name__ == '__main__':
    set_seed(100)
    train_and_test()
"""
        
        # Convert back to list of lines with newlines
        cell['source'] = [line + '\n' for line in new_source.split('\n')][:-1] # Handle the last empty split

with open('digits_classification.new.ipynb', 'w') as f:
    json.dump(nb, f, indent=2)

print("Notebook updated successfully.")
