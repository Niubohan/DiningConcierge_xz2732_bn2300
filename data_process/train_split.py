with open('data/full.csv', 'r') as file:
    lines = [line.strip().split(", ") for line in file.readlines()]

recommend = sorted([line for line in lines if float(line[2]) > 4 and int(line[3]) > 300], key=lambda x: x[2], reverse= True)[:100]
unrecommend = sorted([line for line in lines if float(line[2]) < 4 and int(line[3]) > 300], key=lambda x: x[2])[:100]

with open('data/train_ml.csv', 'w') as file:
    for i in range(100):
        file.writelines('1, ' + ", ".join((recommend[i][2], recommend[i][3])) + '\n')
        file.writelines('0, ' + ", ".join((unrecommend[i][2], unrecommend[i][3])) + '\n')

with open('data/predict_ml.csv', 'w') as file:
    with open('data/test.csv', 'w') as tfile:
        for item in lines:
            if item not in recommend and item not in unrecommend:
                file.writelines(', '.join((item[2], item[3])) + '\n')
                tfile.writelines(', '.join(item) + '\n')
