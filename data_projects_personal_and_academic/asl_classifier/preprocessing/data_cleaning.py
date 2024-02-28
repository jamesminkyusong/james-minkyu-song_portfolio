import asl_classifier.util as util
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import VarianceThreshold

def load_data():
    mnist_train = util.get_path("dataset", "mnist_train_file")
    mnist_test = util.get_path("dataset", "mnist_test_file")
    asl_path = util.get_path("output", "asl_preprocess_post")
    mnist_train_df = pd.read_csv(mnist_train)
    mnist_test_df = pd.read_csv(mnist_test)
    asl_df = pd.read_csv(asl_path)
    return mnist_train_df, mnist_test_df, asl_df


def clean_asl(asl_df):
    asl_df.drop(['ID'], axis=1, inplace=True)  # drop ID column
    label_map = {
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7,
        'i': 8,
        'k': 10,
        'l': 11,
        'm': 12,
        'n': 13,
        'o': 14,
        'p': 15,
        'q': 16,
        'r': 17,
        's': 18,
        't': 19,
        'u': 20,
        'v': 21,
        'w': 22,
        'x': 23,
        'y': 24,
    }  # map for encoding asl labels
    asl_df['label'] = asl_df['label'].map(label_map)

    asl_df = asl_df.sample(frac=1).reset_index(drop=True)  # shuffle rows since sorted by user
    asl_cols = asl_df.columns.tolist()
    asl_cols.insert(2, 'type')  # insert type column to identify between asl and mnist
    asl_df['type'] = "ASL"
    asl_df = asl_df[asl_cols]  # reorder columns
    return asl_df


def clean_mnist(mnist_train_df, mnist_test_df):
    combined_mnist = pd.concat([mnist_train_df, mnist_test_df], axis=0)
    combined_mnist.reset_index(drop=True, inplace=True)

    mnist_cols = combined_mnist.columns.tolist()
    mnist_cols.insert(1, 'PERSON')  # insert PERSON column as a placeholder
    mnist_cols.insert(2, 'type')  # insert type column to identify between asl and mnist

    combined_mnist['PERSON'] = "M"
    combined_mnist['type'] = 'mnist'

    combined_mnist_df = combined_mnist[mnist_cols]  # reorder columns
    return combined_mnist_df

def join_asl_mnist(asl_df, combined_mnist_df):
    combined_df = pd.concat([asl_df, combined_mnist_df], axis=0)
    combined_df.drop(['PERSON'], axis=1, inplace=True) # get rid of person for consistency with MNIST
    combined_df.reset_index(drop=True, inplace=True)
    return combined_df

def standardize_pixel_values(combined_df):
    pixel_columns = combined_df.columns[2:]
    combined_df[pixel_columns] = combined_df[pixel_columns] / 255 # standardize pixel values between 0-1
    return combined_df

def apply_ohe(combined_df):
    labels = combined_df.iloc[:, 0].values.reshape(-1, 1) # 0 is the location of target
    labels_series = pd.Series(labels.ravel())
    unique_labels = labels_series.unique()
    unique_labels.sort()

    ohe = OneHotEncoder(categories=[unique_labels], sparse=False)
    ohe_np_2d = ohe.fit_transform(labels)
    # add ohe cols at the end as new target for multi-classification
    for i, label in enumerate(unique_labels):
        combined_df[f"label_{label}"] = ohe_np_2d[:, i]
    return combined_df

def apply_variance_threshold(combined_df):
    pixel_columns = [col for col in combined_df if col.startswith('pixel')]
    pixel_data = combined_df[pixel_columns]

    selector = VarianceThreshold(threshold=0.05)  # adjust threshold as needed
    reduced_data = selector.fit_transform(pixel_data)

    reduced_data_df = pd.DataFrame(reduced_data, columns=pixel_data.columns[selector.get_support()])
    final_dataset = pd.concat([combined_df.drop(columns=pixel_columns), reduced_data_df], axis=1)

    return final_dataset

def generate_train_test(combined_df):
    trains = []
    tests = []
    labels = combined_df['label'].tolist()
    labels = set(labels)
    for label in labels:
        curr_label_df = combined_df[combined_df['label'] == label]
        train, test = train_test_split(curr_label_df, test_size=0.2, random_state=42)
        trains.append(train)
        tests.append(test)

    train_dataset_final = pd.concat(trains).reset_index(drop=True)
    test_dataset_final = pd.concat(tests).reset_index(drop=True)
    return train_dataset_final, test_dataset_final

def main():
    mnist_train_df, mnist_test_df, asl_df = load_data()
    asl_df = clean_asl(asl_df)
    combined_mnist_df = clean_mnist(mnist_train_df, mnist_test_df)
    combined_df = join_asl_mnist(asl_df, combined_mnist_df)
    combined_df = standardize_pixel_values(combined_df)
    combined_df = apply_ohe(combined_df)
    combined_df = apply_variance_threshold(combined_df)
    train_dataset_final, test_dataset_final = generate_train_test(combined_df)
    util.write_to_csv(train_dataset_final, "output", "train_dataset")
    util.write_to_csv(test_dataset_final, "output", "test_dataset")

if __name__ == "__main__":
    main()