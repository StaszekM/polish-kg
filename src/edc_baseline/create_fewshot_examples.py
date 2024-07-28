import pandas as pd
from src.make_paths_relative_to_root import *
from argparse import ArgumentParser


def create_fewshot_examples(
    random_state: int,
    sample_size: int,
    dataset_path: str,
    schema_path: str,
    reference_path: str,
    oie_fewshot_output_path: str,
    sd_fewshot_output_path: str,
):
    with open(dataset_path) as file:
        series = pd.Series(file.readlines())

    schema = pd.read_csv(schema_path, header=None)

    dataset = pd.DataFrame(series.str.replace("\n", "").tolist(), columns=["text"])

    with open(reference_path) as file:
        series = pd.Series(file.readlines())

    reference = pd.DataFrame(
        series.str.replace("\n", "").tolist(), columns=["reference"]
    )

    dataset = dataset.join(reference)

    sample = dataset.sample(sample_size, random_state=random_state)

    with open(oie_fewshot_output_path, "w") as file:
        for i, (_, data) in enumerate(sample.iterrows()):
            file.write(f"Przykład {i+1}:\n")
            file.write("Tekst: " + str(data["text"]) + "\n")
            file.write("Trójki: " + str(data["reference"]) + "\n")
            file.write("\n")

    sample["reference_relations"] = sample["reference"].apply(lambda x: eval(x))
    sample["reference_relations"] = sample["reference_relations"].map(
        lambda x: [triple[1] for triple in x]
    )

    with open(sd_fewshot_output_path, "w") as file:
        for i, (_, data) in enumerate(sample.iterrows()):
            file.write(f"Przykład {i+1}:\n")
            file.write("Tekst: " + str(data["text"]) + "\n")
            file.write("Trójki: " + str(data["reference"]) + "\n")
            file.write(
                "Relacje: ['" + "', '".join(data["reference_relations"]) + "']\n"
            )
            file.write("Odpowiedź:\n")
            for relation in data["reference_relations"]:
                file.write(
                    f"{relation}: " + schema.loc[schema[0] == relation, 1].item() + "\n"
                )
            file.write("\n")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--random_state", type=int)
    parser.add_argument("--sample_size", type=int)
    parser.add_argument("--dataset_path", type=str)
    parser.add_argument("--schema_path", type=str)
    parser.add_argument("--reference_path", type=str)
    parser.add_argument("--oie_fewshot_output_path", type=str)
    parser.add_argument("--sd_fewshot_output_path", type=str)

    args = parser.parse_args()

    create_fewshot_examples(
        args.random_state,
        args.sample_size,
        args.dataset_path,
        args.schema_path,
        args.reference_path,
        args.oie_fewshot_output_path,
        args.sd_fewshot_output_path,
    )
