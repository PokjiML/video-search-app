def gather_all_unique_objects(videos, get_shots_by_vide):
    all_shots = []
    all_objects = set()
    for v in videos:
        shots = get_shots_by_vide(v['video_id'])
        all_shots.extend(shots)
        for shot in shots:
            objs = shot.get('detected_objects', [])
            normalized_objs = []
            if isinstance(objs, str):
                normalized_objs = [o.strip(" []'\"") for o in objs.split(',') if o.strip(" []'\"")]
            elif isinstance(objs, list):
                for o in objs:
                    if isinstance(o, str):
                        normalized_objs.extend([x.strip(" []'\"") for x in o.split(',') if x.strip(" []'\"")])
            all_objects.update(normalized_objs)
    return sorted(all_objects), all_shots

