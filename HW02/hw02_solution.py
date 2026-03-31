import torch
import matplotlib.pyplot as plt
import csv
import matplotlib.font_manager as fm

# --- 1. Load Taoyuan Dataset ---
ty_years = []
ty_rates = []

with open('桃園市粗出生率.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    for row in reader:
        # Convert ROC year to Western year (ROC year + 1911)
        ty_years.append(float(row[0]) + 1911)
        ty_rates.append(float(row[1]))

# --- 2. Load Kaohsiung Dataset ---
kh_years = []
kh_rates = []

with open('高雄市粗出生率.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    for row in reader:
        kh_years.append(float(row[1])) # Western year
        # Average female and male crude birth rates as an approximation for total
        avg_rate = (float(row[2]) + float(row[3])) / 2.0
        kh_rates.append(avg_rate)

# Convert to tensors
ty_x_raw = torch.tensor(ty_years, dtype=torch.float32)
ty_y = torch.tensor(ty_rates, dtype=torch.float32)

kh_x_raw = torch.tensor(kh_years, dtype=torch.float32)
kh_y = torch.tensor(kh_rates, dtype=torch.float32)

# Normalize/Shift X (Years) based on a common baseline (e.g., 2004)
# This prevents exploding gradients
base_year = 2014.0
ty_x = ty_x_raw - base_year
kh_x = kh_x_raw - base_year

# --- 3. Initialize Parameters & Training Setup ---
# Taoyuan parameters
w1_ty = torch.randn(1, requires_grad=True)
w2_ty = torch.randn(1, requires_grad=True)

# Kaohsiung parameters
w1_kh = torch.randn(1, requires_grad=True)
w2_kh = torch.randn(1, requires_grad=True)

learning_rate = 0.005
epochs = 10000

print("Starting training for Taoyuan & Kaohsiung...")

# --- 4. Training Loop ---
for epoch in range(epochs):
    # Predict
    ty_pred = w1_ty * ty_x + w2_ty
    kh_pred = w1_kh * kh_x + w2_kh
    
    # Calculate Loss
    loss_ty = torch.mean((ty_pred - ty_y) ** 2)
    loss_kh = torch.mean((kh_pred - kh_y) ** 2)
    total_loss = loss_ty + loss_kh
    
    # Back propagation
    total_loss.backward()

    # Update parameters using Gradient Descent
    with torch.no_grad():
        w1_ty -= learning_rate * w1_ty.grad
        w2_ty -= learning_rate * w2_ty.grad
        w1_kh -= learning_rate * w1_kh.grad
        w2_kh -= learning_rate * w2_kh.grad
        
        # Clear gradients
        w1_ty.grad.zero_()
        w2_ty.grad.zero_()
        w1_kh.grad.zero_()
        w2_kh.grad.zero_()
    
    if (epoch + 1) % 500 == 0:
        print(f'Epoch {epoch+1:4d} | TY Loss: {loss_ty.item():.4f} | KH Loss: {loss_kh.item():.4f}')

print(f'\nFinal Taoyuan Parameters:   w1 (slope) = {w1_ty.item():.4f}, w2 (intercept) = {w2_ty.item():.4f}')
print(f'Final Kaohsiung Parameters: w1 (slope) = {w1_kh.item():.4f}, w2 (intercept) = {w2_kh.item():.4f}')

# --- 5. Visualization ---
plt.figure(figsize=(10, 6))

# Plot actual data
plt.scatter(ty_x_raw.numpy(), ty_y.numpy(), color='blue', label='Taoyuan Data', alpha=0.6, marker='o')
plt.scatter(kh_x_raw.numpy(), kh_y.numpy(), color='green', label='Kaohsiung Data', alpha=0.6, marker='s')

# Plot Best Fit Lines
with torch.no_grad():
    ty_line = (w1_ty * ty_x + w2_ty).numpy()
    kh_line = (w1_kh * kh_x + w2_kh).numpy()

plt.plot(ty_x_raw.numpy(), ty_line, color='blue', linestyle='--', label=f'Taoyuan Fit (Slope: {w1_ty.item():.2f})', linewidth=2)
plt.plot(kh_x_raw.numpy(), kh_line, color='green', linestyle='--', label=f'Kaohsiung Fit (Slope: {w1_kh.item():.2f})', linewidth=2)

plt.title("Taoyuan vs Kaohsiung Crude Birth Rates over Time")
plt.xlabel("Year")
plt.ylabel("Crude Birth Rate")
plt.legend()
plt.grid(True)

# Format X-axis ticks as integers
plt.xticks(range(int(min(ty_x_raw).item()), int(max(ty_x_raw).item()) + 2, 2))

plt.tight_layout()
plt.show()
