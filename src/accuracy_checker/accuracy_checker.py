import os
import sys
import argparse
import logging as log
from parameters import parameters
from executors import executor
from process import process
from output import output_handler as out_hand


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file',
        type=str, dest='config_path', required=True)
    parser.add_argument(
        '-m', '--models',
        help='Path to directory in which models and weights declared in config file will be searched',
        type=str, dest='models_path', required=True)
    parser.add_argument(
        '-s', '--source',
        help='Path to directory in which input images will be searched',
        type=str, dest='source_path', required=True)
    parser.add_argument(
        '-r', '--result',
        help='Full name of the resulting file',
        type=str, dest='result_file', required=True)
    parser.add_argument(
        '-a', '--annotations',
        help='Path to directory in which annotation and meta files will be searched',
        type=str, dest='annotations_path', default=None, required=False)
    parser.add_argument(
        '-d', '--definitions',
        help='Path to the global datasets configuration file',
        type=str, dest='definitions_path', default=None, required=False)
    parser.add_argument(
        '-e', '--extensions',
        help='Path to directory with InferenceEngine extensions',
        type=str, dest='extensions_path', default=None, required=False)
    parser.add_argument('--executor_type', type=str, choices=['host_machine', 'docker_container'],
                        help='The environment in which the tests will be executed', default='host_machine')
    config = parser.parse_args().config_path
    if not os.path.isfile(config):
        raise ValueError('Wrong path to configuration file!')
    models = parser.parse_args().models_path
    source = parser.parse_args().source_path
    annotations = parser.parse_args().annotations_path
    definitions = parser.parse_args().definitions_path
    extensions = parser.parse_args().extensions_path
    result = parser.parse_args().result_file
    executor_type = parser.parse_args().executor_type
    return config, models, source, annotations, definitions, extensions, result, executor_type


def accuracy_check(executor_type, test_parameters, output_handler, config, log):
    process_executor = executor.get_executor(executor_type, config, log)
    tests, target_framework = test_parameters.get_config_data()
    test_process = process(log, process_executor, test_parameters)
    test_process.execute(target_framework)
    output_handler.add_results(test_process, tests)
    log.info('Saving test result in file')


def main():
    log.basicConfig(
        format='[ %(levelname)s ] %(message)s',
        level=log.INFO,
        stream=sys.stdout
    )

    try:
        config, models, source, annotations, definitions, extensions, result, executor_type = build_argparser()
        test_parameters = parameters(config, models, source, annotations, definitions, extensions)
        output_handler = out_hand(result)
        output_handler.create_table()
        accuracy_check(executor_type, test_parameters, output_handler, config, log)
    except Exception as ex:
        print('ERROR! : {0}'.format(str(ex)))
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main() or 0)
