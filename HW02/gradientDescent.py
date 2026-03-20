import torch
import matplotlib.pyplot as plt
losses = []

# prepare training data
sizes = torch.tensor([1500, 2000, 1200], dtype=torch.float32)
bedrooms = torch.tensor([3, 4, 2], dtype=torch.float32)
prices = torch.tensor([300000, 400000, 250000], dtype=torch.float32)

# initialize weights
w1 = torch.randn(1, requires_grad=True)
w2 = torch.randn(1, requires_grad=True)

# training 
learning_rate = 0.0000001
epochs = 10000

for epoch in range(epochs):
    # predict price
    predictions = w1 * sizes + w2 * bedrooms
    
    # calculate loss
    loss = torch.mean((predictions - prices) ** 2)
    
    # back propagation
    loss.backward()
    losses.append(loss.item())

    # 
    with torch.no_grad():
        w1 -= learning_rate * w1.grad
        w2 -= learning_rate * w2.grad
        
        # 
        w1.grad.zero_()
        w2.grad.zero_()
    
    if epoch % 1000 == 0:
        print(f'Epoch {epoch+1}, Loss: {loss.item()}')

plt.plot(losses)
plt.xlabel("epoch")
plt.ylabel("loss")
plt.show()

# Weighting
print(f'weighting：w1 = {w1.item()}, w2 = {w2.item()}')
