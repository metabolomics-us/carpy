class TargetAnalyzer:
    def __init__(self, mz_tolerance, rt_tolerance, log):
        self.mz_tolerance = mz_tolerance
        self.rt_tolerance = rt_tolerance
        self.log = log

    @staticmethod
    def build_target_identifier(target):
        return f"{target['name']}_{target['retentionTimeInSeconds'] / 60:.1f}_{target['mass']:.1f}"

    def build_target_list(self, targets, sample, intensity_filter=0):
        if 'error' in sample:
            if self.log:
                print('Error:', sample)
            return targets

        start_index = 0
        new_targets = []

        # Lookup for target names
        # Commented version for future when target RT m/z has been corrected
        # target_lookup = {self.build_target_identifier(x): x['id'] for x in targets if x['name'] != 'Unknown'}
        target_lookup = {x['name']: x['id'] for x in targets if x['name'] != 'Unknown'}

        # Get all annotations and sort by mass
        annotations = sum([v['results'] for v in sample['injections'].values()], [])
        annotations.sort(key=lambda x: x['target']['mass'])

        max_intensity = max(x['annotation']['intensity'] for x in annotations)

        # Avoid duplicate targets
        observed_targets = set()

        # Match all targets in sample data to master target list
        for x in annotations:
            # For now, horrible hack to handle duplicate targets
            if x['target']['name'] != 'Unknown':
                if x['target']['name'] in observed_targets:
                    continue
                observed_targets.add(x['target']['name'])

            # target_identifier = self.build_target_identifier(x['target'])
            target_identifier = x['target']['name']

            if target_identifier in target_lookup:
                x['target']['id'] = target_lookup[target_identifier]
                continue

            matched = False
            ri = x['target']['retentionTimeInSeconds']

            for i in range(start_index, len(targets)):
                if targets[i]['mass'] < x['target']['mass'] - self.mz_tolerance:
                    start_index = i + 1
                    continue
                if targets[i]['mass'] > x['target']['mass'] + self.mz_tolerance:
                    break

                if ri - self.rt_tolerance <= targets[i]['retentionTimeInSeconds'] <= ri + self.rt_tolerance:
                    if self.log:
                        print(f"Matched ({x['target']['name']}, {ri}, {x['target']['mass']}) -> ({targets[i]['id']},"
                              f"{targets[i]['name']}, {targets[i]['retentionTimeInSeconds']}, {targets[i]['mass']})")

                    x['target']['id'] = targets[i]['id']
                    matched = True
                    break

            if not matched:
                if x['annotation']['intensity'] >= intensity_filter * max_intensity:
                    t = x['target']
                    t['id'] = len(targets) + len(new_targets) + 1
                    new_targets.append(t)
                else:
                    if self.log:
                        print(f"Skipped feature ({x['target']['name']}, {ri}, {x['target']['mass']}, "
                              f"{x['annotation']['intensity']}), "
                              f"less than {intensity_filter * 100}% base peak intensity")

        return sorted(targets + new_targets, key=lambda x: x['mass'])
