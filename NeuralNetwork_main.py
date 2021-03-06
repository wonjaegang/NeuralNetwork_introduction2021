from extraFunctions import *
from timeit import default_timer as timer


class Layer:
    def __init__(self, size, lastLayer):
        self.size = size
        # If it is an input layer
        if not lastLayer:
            # 입력값들로 이루어진 열벡터 A
            self.A = []
        # If it is not
        else:
            self.lastLayer = lastLayer

            # 레이어 노드들의 편향값들로 이루어진 열벡터 B
            self.B = randomList(size, -1, 1)

            # 이전 레이어와 연결되는 신경망들의 가중치들로 이루어진 (thisLayer size) * (lastLayer size) 크기의 행렬 W
            self.W = [randomList(lastLayer.size, -1, 1) for _ in range(size)]

            # 레이어 노드들의 활성화함수 입력값들로 이루어진 열벡터 Z
            self.Z = [0 for _ in range(size)]

            # 레이어 노드들의 활성화함수 출력값들로 이루어진 열벡터 A
            self.A = [0 for _ in range(size)]

            # 비용함수의 노드값들에 대한 편미분값으로 이루어진 열벡터 dC_dA
            self.dC_dA = [0 for _ in range(size)]

            # 비용함수의 가중치값들에 대한 편미분값으로 이루어진 (thisLayer size) * (lastLayer size) 크기의 행렬 dC_dA
            self.dC_dW = [[0 for _ in range(lastLayer.size)] for _ in range(size)]

            # 비용함수의 편향값들에 대한 편미분값으로 이루어진 열벡터 dC_dA
            self.dC_dB = [0 for _ in range(size)]

    # Z(n) =  W(n, n-1) * A(n-1) + B(n)
    # A(n) = k(Z(n)), k(x)는 활성화 함수
    def feedForward(self):
        Z = []
        for nodeIndex in range(self.size):
            temp = 0
            for lastNodeIndex in range(self.lastLayer.size):
                temp += self.W[nodeIndex][lastNodeIndex] * self.lastLayer.A[lastNodeIndex]
            z = temp + self.B[nodeIndex]
            Z.append(z)
        A = list(map(lambda x: k(x), Z))
        self.Z = Z
        self.A = A

    def feedBackward(self):
        # dC/dW(k) = dC/dA * dA/dW(k) = dC/dA * k'(Z) * lastLayer.A[k]
        dC_dW = []
        for nodeIndex in range(self.size):
            dC_dW_k = []
            for lastNodeIndex in range(self.lastLayer.size):
                temp = self.dC_dA[nodeIndex] * dk(self.Z[nodeIndex]) * self.lastLayer.A[lastNodeIndex]
                average = calculateAverage(self.dC_dW[nodeIndex][lastNodeIndex], dataIndex + 1, temp)
                dC_dW_k.append(average)
            dC_dW.append(dC_dW_k)
        self.dC_dW = dC_dW

        # dC/dB = dC/dA * dA/dB = dC/dA * k'(Z)
        dC_dB = []
        for nodeIndex in range(self.size):
            temp = self.dC_dA[nodeIndex] * dk(self.Z[nodeIndex])
            average = calculateAverage(self.dC_dB[nodeIndex], dataIndex + 1, temp)
            dC_dB.append(average)
        self.dC_dB = dC_dB

        # dC/d(lastLayer.A) = dC/dA * dA/d(lastLayer.A) = dC/dA * k'(Z) * W
        last_dC_dA = []
        for lastNodeIndex in range(self.lastLayer.size):
            temp = 0
            for nodeIndex in range(self.size):
                temp += self.dC_dA[nodeIndex] * dk(self.Z[nodeIndex]) * self.W[nodeIndex][lastNodeIndex]
            last_dC_dA.append(temp)
        self.lastLayer.dC_dA = last_dC_dA

    # updated X = X - learningRate * dC/dX
    def updateNeurons(self):
        for nodeIndex in range(self.size):
            for lastNodeIndex in range(self.lastLayer.size):
                self.W[nodeIndex][lastNodeIndex] -= setting.learningRate * self.dC_dW[nodeIndex][lastNodeIndex]

        for nodeIndex in range(self.size):
            self.B[nodeIndex] -= setting.learningRate * self.dC_dB[nodeIndex]


class Setting:
    def __init__(self):
        self.epoch = 10
        self.inputDataSize = 1000
        self.evaluationDataSize = 1000
        self.learningRate = 0.5


# 하나의 입력-출력 데이터 셋을 파일에 입력
def createDataSet(file):
    inputList = randomList(inputLayer.size, 0, 1)
    for inputNum in inputList:
        file.write("%f " % inputNum)
    file.write(",")
    outputList = expectedOutput(inputList)
    for outputNum in outputList:
        file.write("%f " % outputNum)
    file.write("\n")


# 입력 데이터 파일을 생성
def createInputDataFile():
    with open("Data/InputData.txt", 'w') as f:
        for _ in range(setting.inputDataSize):
            createDataSet(f)


# 평가용 데이터 파일을 생성
def createEvaluationDataFile():
    with open("Data/EvaluationData.txt", 'w') as f:
        for _ in range(setting.evaluationDataSize):
            createDataSet(f)


# 데이터셋 파일로부터 입력/출력 리스트 추출
def readData(fileName, index):
    with open(fileName, 'r') as f:
        for i, line in enumerate(f):
            if i == index:
                split = line.split(',')
                inputData = list(map(lambda x: float(x), split[0].split(' ')[:-1]))
                outputData = list(map(lambda x: float(x), split[1].split(' ')[:-1]))
                return inputData, outputData


# 활성화 함수(Activation function)
def k(x):
    y = sigmoid(x)
    return y


# 활성화 함수의 도함수
def dk(x):
    y = derivativeSigmoid(x)
    return y


# 입력값의 평균값이 0.5 미만이면 [1, 0]을, 이상이면 [0, 1]을 반환한다.
def expectedOutput(inputList):
    if sum(inputList) < inputLayer.size / 2:
        return [0, 0]
    else:
        return [1, 1]


# C(y) = 1/n * sum( (setPoint - Y)^2 )
# 비용함수는 오차의 제곱들의 평균값
def costFunc():
    errorAverage = 0
    for index in range(outputLayer.size):
        error = (expectedOutput(inputLayer.A)[index] - outputLayer.A[index]) ** 2
        errorAverage = calculateAverage(errorAverage, index + 1, error)
    return errorAverage


# dC/dY = -2/n * (setPoint - Y)
# 출력 레이어에서의 dC/dA는 비용함수의 출력값 Y에 대한 편미분 값
def get_dC_dY(setPoint):
    dC_dY = []
    for nodeIndex in range(outputLayer.size):
        temp = -2 / outputLayer.size * (setPoint[nodeIndex] - outputLayer.A[nodeIndex])
        dC_dY.append(temp)
    return dC_dY


# 테스트 데이터 셋으로 신경망 평가
def evaluateNeurons():
    correctAnswer = 0
    averageCost = 0
    for dataIndex_test in range(setting.evaluationDataSize):
        extractedData_test = readData("Data/EvaluationData.txt", dataIndex_test)
        inputDataList_test = extractedData_test[0]
        outputDataList_test = extractedData_test[1]

        inputLayer.A = inputDataList_test
        layer1.feedForward()
        layer2.feedForward()
        outputLayer.feedForward()

        digitalOutput = list(map(lambda x: analog2digital(x), outputLayer.A))
        if digitalOutput == outputDataList_test:
            correctAnswer += 1

        averageCost = calculateAverage(averageCost, dataIndex_test + 1, costFunc())
    return correctAnswer / setting.evaluationDataSize, averageCost


# 각 epoch 마다 신경망평가 결과를 출력하고 파일로 저장
def recordEvaluationResult():
    print("Epoch #%d Accuracy: %.2f%%, Cost: %f, Running Time: %fsec"
          % (epochIndex + 1, accuracy * 100, cost, runningTime))
    with open("Data/TestResultData.txt", 'a' if epochIndex else 'w') as f:
        f.write("%f, %f, %f" % (accuracy, cost, runningTime))
        f.write("\n")


# 학습된 신경망의 정보를 파일로 저장
def recordNeurons():
    def writeNeuronData(layer):
        for Wi in layer.W:
            for Wik in Wi:
                f.write("%s " % str(Wik))
            f.write("\n")
        for b in layer.B:
            f.write("%s " % str(b))
        f.write("\n")
    with open("Data/learnedNeuronData.txt", 'w') as f:
        writeNeuronData(layer1)
        writeNeuronData(layer2)
        writeNeuronData(outputLayer)


# 학습된 신경망의 정보를 파일에서 추출
def loadNeurons(fileName):
    def extractNeuronData(layer):
        layerData_W = []
        lines = [f.readline() for _ in range(layer.size)]
        for line in lines:
            WList = list(map(lambda x: float(x), line.split(' ')[:-1]))
            layerData_W.append(WList)
        layerData_B = list(map(lambda x: float(x), f.readline().split(' ')[:-1]))
        return layerData_W, layerData_B
    with open(fileName, 'r') as f:
        layer1Data = extractNeuronData(layer1)
        layer2Data = extractNeuronData(layer2)
        outputLayerData = extractNeuronData(outputLayer)
        return layer1Data, layer2Data, outputLayerData


if __name__ == "__main__":
    setting = Setting()

    inputLayer = Layer(10, False)
    layer1 = Layer(4, inputLayer)
    layer2 = Layer(4, layer1)
    outputLayer = Layer(2, layer2)

    createInputDataFile()
    createEvaluationDataFile()

    for epochIndex in range(setting.epoch):
        epochStartTime = timer()

        for dataIndex in range(setting.inputDataSize):
            # 데이터 셋에서 이번 인덱스의 데이터 추출
            extractedData = readData("Data/InputData.txt", dataIndex)
            inputDataList = extractedData[0]
            outputDataList = extractedData[1]

            # 입력 데이터로 노드값 계산
            inputLayer.A = inputDataList
            layer1.feedForward()
            layer2.feedForward()
            outputLayer.feedForward()

            # 오차역전파
            outputLayer.dC_dA = get_dC_dY(outputDataList)
            outputLayer.feedBackward()
            layer2.feedBackward()
            layer1.feedBackward()

        # 가중치와 편향값의 gradient 방향 조정
        layer1.updateNeurons()
        layer2.updateNeurons()
        outputLayer.updateNeurons()

        # 테스트 데이터 셋으로 신경망의 정확도 계산
        evaluated = evaluateNeurons()
        accuracy = evaluated[0]
        cost = evaluated[1]

        # 한 epoch 의 실행시간 계산
        epochFinishTime = timer()
        runningTime = epochFinishTime - epochStartTime

        # 신경망평가 결과를 출력하고 파일로 저장
        recordEvaluationResult()

    # 학습된 신경망 데이터를 파일로 저장
    recordNeurons()

    neuronData = loadNeurons("Data/learnedNeuronData.txt")
    print("layer1 Weight data:", neuronData[0][0])
    print("layer1 Bias data:", neuronData[0][1])

    # TODO: 다른 입력/출력도 해봐야함. 리니어하지 않은걸로
    # TODO: 다양한 방법의 경사구배를 사용해보자.
    # TODO: 출력함수와 활성화함수를 구분하자.
