"""
    This is an example on how a PyTorch script can be used.
    The following code is adapted from a tutorial provided by PyTorch.
    Source: https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
"""
import base64
import io
import matplotlib
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from PIL import Image
from werkzeug.datastructures import FileStorage
import matplotlib.pyplot as plt

# for backend matplotlib
matplotlib.use('Agg')

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

ALLOWED_EXTENSIONS = ["png", "jpg", "bmp"]

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def train_model():
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    batch_size = 4

    trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                            download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                              shuffle=True, num_workers=0)

    net = Net()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data

            optimizer.zero_grad()

            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    print('Finished Training')

    PATH = './cifar_net.pth'
    torch.save(net.state_dict(), PATH)


def predict_image(image):
    transform = transforms.Compose(
        [transforms.Resize((32, 32)),
         transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    img = Image.open(io.BytesIO(image))
    img = transform(img)
    img = img.unsqueeze(0)
    net = Net()
    # change this path
    PATH = './modules/pytorch_example/cifar_net.pth'
    net.load_state_dict(torch.load(PATH))
    net.eval()

    with torch.no_grad():
        output = net(img)
        _, predicted = torch.max(output, 1)
        predicted_class = predicted.item()

    predict_result = "Predicted class: " + classes[predicted_class-1]

    img = Image.open(io.BytesIO(image))
    plt.figure(figsize=(6, 6))
    plt.imshow(img)
    plt.title(predict_result)
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    img_src = f"data:image/png;base64,{img_base64}"

    return [[img_src, "/static/img/image.jpg", "/static/img/image.jpg"], predict_result]


def validate(image_field1):
    if type(image_field1) is FileStorage:
        filename = image_field1.filename
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            return predict_image(image_field1)
    elif type(image_field1) is bytes:
        return predict_image(image_field1)
    else:
        return False