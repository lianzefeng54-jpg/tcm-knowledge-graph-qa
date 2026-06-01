from __002__extract_information.__000__extract_graph_data_utils import extract_from_folder
from common.path_utils import get_file_path

extract_from_folder(get_file_path("__001__clawler/中药"),
                    get_file_path("__002__extract_information/extract_herb_data.json"),
                    get_file_path("__002__extract_information/extract_herb_finetune_data.json"))
