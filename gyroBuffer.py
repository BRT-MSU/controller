

class GyroBuffer():
    def __init__(self, size):
        self.buffer = [0.0] * size

    def add(self, element):
        self.buffer.append(element)
        self.buffer.pop(0)

    def computeAverage(self):
        sum = 0.0
        for element in self.buffer:
            sum += element

        return sum / len(self.buffer)


if __name__ == '__main__':
    gyroBuffer = GyroBuffer(5)

    gyroBuffer.add(1.5)
    gyroBuffer.add(2.5)
    gyroBuffer.add(3.5)
    gyroBuffer.add(4.5)
    gyroBuffer.add(5.5)
    gyroBuffer.add(6.5)

    print gyroBuffer.buffer

    print gyroBuffer.buffer[-2]

    print gyroBuffer.computeAverage()