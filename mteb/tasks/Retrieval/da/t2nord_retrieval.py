import datasets

from mteb.abstasks import AbsTaskRetrieval, TaskMetadata


class TV2Nordretrieval(AbsTaskRetrieval):
    metadata = TaskMetadata(
        name="TV2Nordretrieval",
        hf_hub_name="alexandrainst/nordjylland-news-summarization",
        description="News Article and corresponding summaries extracted from the Danish newspaper TV2 Nord.",
        reference="https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization",
        type="Retrieval",
        category="p2p",
        eval_splits=["test"],
        eval_langs=["da"],
        main_score="ndcg_at_10",
        revision="80cdb115ec2ef46d4e926b252f2b59af62d6c070",
        date=("2020-01-01", "2024-12-31"),  # best guess
        form=["written"],
        domains=["News", "Non-fiction"],
        license="CC0",
        socioeconomic_status="high",
        annotations_creators="derived",
        dialect=[],
        text_creation="found",
        bibtex_citation=None,
        n_samples={"test": 4096},
        avg_character_length={"test": 784.11},
        task_subtypes=["Article retrieval"],
    )

    def load_data(self, **kwargs: dict):  # noqa: ARG002
        """
        Load dataset from HuggingFace hub
        """
        if self.data_loaded:
            return

        self.dataset: datasets.DatasetDict = datasets.load_dataset(
            self.metadata_dict["hf_hub_name"],
            revision=self.metadata_dict.get("revision"),
        )  # type: ignore

        self.dataset_transform()
        self.data_loaded = True

    def dataset_transform(self) -> None:
        """
        and transform to a retrieval datset, which have the following attributes

        self.corpus = Dict[doc_id, Dict[str, str]] #id => dict with document datas like title and text
        self.queries = Dict[query_id, str] #id => query
        self.relevant_docs = Dict[query_id, Dict[[doc_id, score]]
        """
        self.corpus = {}
        self.relevant_docs = {}
        self.queries = {}
        text2id = {}

        for split in self.dataset:
            ds: datasets.Dataset = self.dataset[split]  # type: ignore
            ds = ds.shuffle(seed=42)
            ds = ds.select(
                range(2048)
            )  # limit the dataset size to make sure the task does not take too long to run
            self.queries[split] = {}
            self.relevant_docs[split] = {}
            self.corpus[split] = {}

            summary = ds["summary"]
            article = ds["text"]

            n = 0
            for summ, art in zip(summary, article):
                self.queries[split][str(n)] = summ
                q_n = n
                n += 1
                if art not in text2id:
                    text2id[art] = n
                    self.corpus[split][str(n)] = {"title": "", "text": art}
                    n += 1

                self.relevant_docs[split][str(q_n)] = {
                    str(text2id[art]): 1
                }  # only one correct matches
