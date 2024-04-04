import os
import sys
import argparse
from sklearn.metrics import classification_report


# Input validation
def dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            "Path '{}' is not a directory".format(path))
    return path


def parseArguments(sysArgs):
    parser = argparse.ArgumentParser(
        description="""Evaluate BIO formatted entity labels against a Golden Standard (also BIO formatted).
                    Note that the script expects the Predicted entitites and the Golden Standard to be in 
                    files of the same name, with extension .bio""")

    parser.add_argument(
        '--gold_dir',
        dest='gold_dir', required=True, type=dir,
        help="The directory that the Golden Standard is in")

    parser.add_argument(
        '--pred_dir',
        dest='pred_dir', required=True, type=dir,
        help="The directory that the predicted entities are in")


    parsedArgs = parser.parse_args()

    return parsedArgs

def evaluate_file(gold_file, pred_file):
    gold_labels = extract_labels(gold_file)
    pred_labels = extract_labels(pred_file)
    return get_report(gold_labels, pred_labels)


def main(args):
    args = parseArguments(args)
    
    reports = []
    gold_dir = args.gold_dir
    pred_dir = args.pred_dir

    for pred_file_name in os.listdir(pred_dir):
        if pred_file_name.endswith(".bio"):
            pred_file_path = os.path.join(pred_dir, pred_file_name)
            gold_file_path = os.path.join(gold_dir, pred_file_name)

            if os.path.exists(gold_file_path):
                report = evaluate_file(gold_file_path, pred_file_path)
                reports.append(report)

    process_reports(reports)


def process_reports(reports):
    ras = []

    for report in reports:
        for type, values in report.items():
            if type in ['LOC', 'PER', 'ORG', 'OTH', 'O']:
                existing_ra = next((ra for ra in ras if ra.type == type), None)
                
                if not existing_ra:
                    ras.append(ReportAverager(type, values))
                else:
                    existing_ra.add(values)

    sorted_ras = sorted(ras)
    pretty_print(sorted_ras)


def pretty_print(report_averagers):
    name_width = max(len(cn.type) for cn in report_averagers)
    width = max(name_width, 3, 3)
    head_fmt = '{:>{width}s} ' + ' {:>9}' * 3
    report = '\n\n'
    report += head_fmt.format('', 'precision', 'recall',
                             'f1-score', width=width)
    report += '\n\n'
    row_fmt = '{:>{width}s} ' + ' {:>9.{digits}f}' * 3 + ' \n'

    o_row = None
    for ra in report_averagers:
        if ra.type == "O":
            o_row = row_fmt.format(ra.type, ra.get_precision(
            ), ra.get_recall(), ra.get_f1score(), width=width, digits=3)
        else:
            report += row_fmt.format(ra.type, ra.get_precision(),
                                     ra.get_recall(), ra.get_f1score(), width=width, digits=3)
    report += o_row
    report += '\n'
    print(report)


class ReportAverager:
    def __init__(self, type, values):
        self.type = type
        self.reports = [values]

    def __eq__(self, other):
        return self.type == other.type

    def __lt__(self, other):
        return self.type<other.type

    def add(self, report):
        self.reports.append(report)

    def get_precision(self):
        total = self.get_total('precision')
        if total == 0.00:
            return total
        return total / len(self.reports)

    def get_recall(self):
        total = self.get_total('recall')
        if total == 0.00:
            return total
        return total / len(self.reports)

    def get_f1score(self):
        total = self.get_total('f1-score')
        if total == 0.00:
            return total
        return total / len(self.reports)

    def get_total(self, property_name):
        total = 0.00
        for report in self.reports:
            total = total + report[property_name]
        return total


def get_report(gold_labels, pred_labels):
    '''
    Get a report much like this:
    
    { 
        'LOC': {
            'precision': 1.0, 
            'recall': 0.5, 
            'f1-score': 0.6666666666666666, 
            'support': 2
        }, 
        'PER': {
            'precision': 1.0, 
            'recall': 1.0, 
            'f1-score': 1.0, 
            'support': 1
        },
        'O': {
            'precision': 0.6666666666666666, 
            'recall': 1.0, 
            'f1-score': 0.8, 
            'support': 2
        }, 
        'accuracy': 0.8333333333333334, 
        'macro avg': {
            'precision': 0.9166666666666666, 
            'recall': 0.875, 
            'f1-score': 0.8666666666666667, 
            'support': 6
        }, 
        'weighted avg': {
            'precision': 0.8888888888888888, 
            'recall': 0.8333333333333334, 
            'f1-score': 0.8222222222222223, 
            'support': 6
        }
    }
    '''
    return classification_report(gold_labels, pred_labels, output_dict=True)


def extract_labels(file):
    labels = []

    with open(file, 'r') as fh:
        for line in fh.readlines():
            if 'LOC' in line:
                labels.append('LOC')
                continue
            if 'PER' in line:
                labels.append('PER')
                continue
            if 'ORG' in line:
                labels.append('ORG')
                continue
            if 'OTHER' in line or 'OTH' in line:
                labels.append('OTH')
                continue

            labels.append('O')

    return labels


if __name__ == '__main__':
    sys.exit(main(sys.argv))
