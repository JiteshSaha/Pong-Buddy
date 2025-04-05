import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from safetensors.torch import save_file
import joblib

data = pd.read_csv("./pong_training_data.csv")

# features = ["ball_x", "ball_y", "ball_dx", "ball_dy", "paddle1_y", "paddle2_y", "paddle2_action", "score1", "score2"]
label = "paddle2_action"
features = ["ball_x", "ball_y", "ball_dx", "ball_dy", "paddle1_y", "paddle2_y", "paddle2_action"]

# Ensure labels are valid for CrossEntropyLoss
data["paddle1_action"] = data["paddle1_action"].map({-1: 0, 0: 1, 1: 2})
data["paddle2_action"] = data["paddle2_action"].map({-1: 0, 0: 1, 1: 2})

x = data[features].values
y = data[label].values

scaler = StandardScaler()
X = scaler.fit_transform(x)

x_train, x_test, y_train, y_test = train_test_split(X,y, test_size=0.3,random_state=42)


X_train = torch.tensor(x_train, dtype=torch.float32)
X_test = torch.tensor(x_test, dtype=torch.float32)
Y_train = torch.tensor(y_train, dtype=torch.int64)
Y_test = torch.tensor(y_test, dtype=torch.int64)


class PongAI(torch.nn.Module):

    def __init__(self) -> None:
            super().__init__()
            self.fc1 = nn.Linear(len(features),64)
            self.fc2 = nn.Linear(64, 32)
            self.fc3 = nn.Linear(32, 3)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
    



model = PongAI()
criteron = torch.nn.CrossEntropyLoss()
optim = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 100

for epoch in range(epochs):
    
    optim.zero_grad()
    outputs = model(X_train)
    loss = criteron(outputs, Y_train)

    loss.backward()
    optim.step()

    print(f"Epoch: {epoch+1}/{epochs} , Loss: {loss.item():.4f}")

# Evaluate on test data
with torch.no_grad():
    test_outputs = model(X_test)
    predictions = torch.argmax(test_outputs, axis=1)
    accuracy = (predictions == y_test).sum().item() / len(y_test)
    print(f"Test Accuracy: {accuracy:.2f}")


# Save model
state_dict = model.state_dict()
save_file(state_dict, "pong_ai_model.safetensors")
print("Model saved as pong_ai_model.safetensors")

joblib.dump(scaler, "scaler.pkl")

