import torch
import torch.nn.functional as F

y = torch.tensor([1.0])
x1 = torch.tensor([1.1])
w1 = torch.tensor([2.2])
b = torch.tensor([0.0])
z = x1 * w1 + b
a = torch.sigmoid(z)
loss = F.binary_cross_entropy(a, y)
print(loss)

from  torch.autograd import grad
y = torch.tensor([1.0])
x1 = torch.tensor([1.1])
w1 = torch.tensor([2.2], requires_grad=True)
b = torch.tensor([0.0], requires_grad=True)

z = x1 * w1 + b
a = torch.sigmoid(z)

loss = F.binary_cross_entropy(a, y)

# use the grad function manually to calculate the gradient of loss with respect to w1 and b
grad_L_w1 = grad(loss, w1, retain_graph=True)
grad_L_b = grad(loss, b, retain_graph=True)

print(grad_L_w1)
print(grad_L_b)

# high level tools to automate this process
loss.backward()
print(w1.grad)
print(b.grad)

class NeuralNetwork(torch.nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super().__init__()

        self.layers = torch.nn.Sequential(

            # 1st hidden layer
            torch.nn.Linear(num_inputs, 30),
            torch.nn.ReLU(),

            # 2nd hidden layer
            torch.nn.Linear(30, 20),
            torch.nn.ReLU(),

            # output layer
            torch.nn.Linear(20, num_outputs),
        )
    
    def forward(self, x):
        logits = self.layers(x)
        return logits

model = NeuralNetwork(50, 3)
print(model)

num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print("Total number of trainable model parameters:", num_params)
print(model.layers[0].weight)
print(model.layers[0].weight.shape)

# make the random number initialization reproducible by seeding PyTorch’s random number generator via manual_seed
torch.manual_seed(123)
model = NeuralNetwork(50, 3)
print(model.layers[0].weight)

torch.manual_seed(123)
X = torch.rand((1,50))
out = model(X)
print(out)

with torch.no_grad():
    out = torch.softmax(model(X), dim=1)
print(out)

# setting up efficient data loaders
X_train = torch.tensor([
    [-1.2, 3.1],
    [-0.9, 2.9],
    [-0.5, 2.6],
    [2.3, -1.1],
    [2.7, -1.5]
])
y_train = torch.tensor([0, 0, 0, 1, 1])

X_test = torch.tensor([
    [-0.8, 2.8],
    [2.6, -1.6],
])
y_test = torch.tensor([0, 1])

from torch.utils.data import Dataset

class ToyDataset(Dataset):
    def __init__(self, X, y):
        self.features = X
        self.labels = y

    def __getitem__(self, index):
        one_x = self.features[index]
        one_y = self.labels[index]
        return one_x, one_y

    def __len__(self):
        return self.labels.shape[0]

train_ds = ToyDataset(X_train, y_train)
test_ds = ToyDataset(X_test, y_test)

print(len(train_ds))

from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset = train_ds,
    batch_size = 2,
    shuffle = True,
    num_workers = 0
)

test_loader = DataLoader(
    dataset = test_ds,
    batch_size = 2,
    shuffle = False,
    num_workers = 0
)

for idx, (x, y) in enumerate(train_loader):
    print(f"Batch {idx + 1}:", x, y)

train_loader = DataLoader(
    dataset = train_ds,
    batch_size = 2,
    shuffle = True,
    num_workers = 0,
    drop_last = True
)

for idx, (x, y) in enumerate(train_loader):
    print(f"Batch {idx + 1}:", x, y)

# a typical training loop
import torch.nn.functional as F 

torch.manual_seed(123)
model = NeuralNetwork(num_inputs=2, num_outputs=2)
optimizer = torch.optim.SGD(model.parameters(), lr=0.5)

num_epochs = 3
for epoch in range(num_epochs):
    model.train()
    for batch_idx, (features, labels) in enumerate(train_loader):
        logits = model(features)

        loss = F.cross_entropy(logits, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        ### LOGGING
        print(f"Epoch: {epoch+1:03d}/{num_epochs:03d}"
                f" | Batch {batch_idx:03d}/{len(train_loader):03d}"
                f" | Train Loss: {loss:.2f}")
    
    model.eval()
    # Insert optional model evaluation code  

model.eval()
with torch.no_grad():
    outputs = model(X_train)
print(outputs)

torch.set_printoptions(sci_mode=False)
probas = torch.softmax(outputs, dim=1)
print(probas)

predictions = torch.argmax(probas, dim=1)
print(predictions)

predictions = torch.argmax(probas, dim=0)
print(predictions)

predictions = torch.argmax(outputs, dim=1)
print(predictions)

print(predictions == y_train)

print(torch.sum(predictions == y_train))

def compute_accuracy(model, dataloader):
    model = model.eval()
    correct = 0.0
    total_examples = 0

    for idx, (features, labels) in enumerate(dataloader):

        with torch.no_grad():
            logits = model(features)

        predictions = torch.argmax(logits, dim = 1)
        compare = labels == predictions
        correct += torch.sum(compare)
        total_examples += len(compare)

    return (correct / total_examples).item()

print(compute_accuracy(model, train_loader))
print(compute_accuracy(model, test_loader))