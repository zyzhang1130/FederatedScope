import os
import sys

DEV_MODE = True  # simplify the federatedscope re-setup everytime we change the source codes of federatedscope
if DEV_MODE:
    file_dir = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(file_dir)

from yacs.config import CfgNode
from federatedscope.core.cmd_args import parse_args
from federatedscope.core.auxiliaries.data_builder import get_data
from federatedscope.core.auxiliaries.utils import setup_seed, update_logger
from federatedscope.core.auxiliaries.worker_builder import get_client_cls, get_server_cls
from federatedscope.core.configs.config import global_cfg
from federatedscope.core.fed_runner import FedRunner

if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']


if __name__ == '__main__':
    init_cfg = global_cfg.clone()
    args = parse_args()
    init_cfg.merge_from_file(args.cfg_file)
    init_cfg.merge_from_list(args.opts)
    update_logger(init_cfg)
    setup_seed(init_cfg.seed)

    data, modified_cfg = get_data(config=init_cfg.clone())
    init_cfg.merge_from_other_cfg(modified_cfg)
    init_cfg.freeze()

    # allow different settings for different clients
    if args.cfg_client is None:
        cfg_client = None
    else:
        cfg_client = CfgNode.load_cfg(open(args.cfg_client, 'r'))

    runner = FedRunner(data=data,
                       server_class=get_server_cls(init_cfg),
                       client_class=get_client_cls(init_cfg),
                       config=init_cfg.clone(),
                       config_client=cfg_client)
    _ = runner.run()
