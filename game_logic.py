import random
from shapely.geometry import Point, LineString


class GameLogic:
    def __init__(
        self,
        countries_data,
        rivers_data,
        oceans_data,
        mountains_data,
        continents_data,
        world_blocks_data,
    ):
        self.score = 0
        self.countries = countries_data
        self.rivers = rivers_data
        self.oceans = oceans_data
        self.mountains = mountains_data
        self.continents = continents_data
        self.world_blocks = world_blocks_data
        self.bbox_list = self._extract_bounding_boxes()
        self.continents_bbox = self._calculate_combined_bboxes(self.continents)
        self.world_blocks_bbox = self._calculate_combined_bboxes(self.world_blocks)
        self.asked_item = None
        self.game_mode = None
        self.hard_mode = False

    def _extract_bounding_boxes(self):
        bbox_list = {}
        for country, data in self.countries.items():
            if "bbox" in data:
                bbox_list[country] = [
                    list(country_obj.bbox) for country_obj in data["bbox"]
                ]
        return bbox_list

    def _calculate_combined_bboxes(self, regions):
        combined_bboxes = {}
        for region_name, country_list in regions.items():
            bboxes = []
            for country_name in country_list:
                if country_name in self.bbox_list:
                    bboxes.extend(self.bbox_list[country_name])
            if bboxes:
                combined_bboxes[region_name] = bboxes
        return combined_bboxes

    def set_game_mode(self, mode):
        self.game_mode = mode
        self.score = 0

    def start_new_round(self):
        self.ask_random_item()

    def get_item_from_coordinates(self, lon, lat):
        if self.game_mode == "countries":
            for country, bboxes in self.bbox_list.items():
                for bbox in bboxes:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                        return country
        elif self.game_mode == "rivers":
            point = Point(lon, lat)
            for river, data in self.rivers.items():
                line = LineString(data["coordinates"])
                if point.distance(line) < 0.5:
                    return river
        elif self.game_mode == "oceans":
            clicked_oceans = []
            for ocean, data in self.oceans.items():
                min_lon, min_lat, max_lon, max_lat = data["bbox"]
                if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                    clicked_oceans.append(ocean)

            if not clicked_oceans:
                return None
            if len(clicked_oceans) == 1:
                return clicked_oceans[0]

            # If the click is in multiple bounding boxes, find the closest center
            closest_ocean = None
            min_dist = float("inf")
            for ocean_name in clicked_oceans:
                ocean_data = self.oceans[ocean_name]
                center_lon = (ocean_data["bbox"][0] + ocean_data["bbox"][2]) / 2
                center_lat = (ocean_data["bbox"][1] + ocean_data["bbox"][3]) / 2
                dist = ((lon - center_lon) ** 2 + (lat - center_lat) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_ocean = ocean_name
            return closest_ocean
        elif self.game_mode == "mountains":
            for mountain, data in self.mountains.items():
                min_lon, min_lat, max_lon, max_lat = data["bbox"]
                if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                    return mountain
        elif self.game_mode == "continents":
            clicked_continents = []
            for continent, bboxes in self.continents_bbox.items():
                for bbox in bboxes:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                        clicked_continents.append(continent)
                        break

            if not clicked_continents:
                return None
            if len(clicked_continents) == 1:
                return clicked_continents[0]

            # If the click is in multiple bounding boxes, find the one with the smallest area
            smallest_area = float("inf")
            best_continent = None
            for continent_name in clicked_continents:
                area = 0
                for bbox in self.continents_bbox[continent_name]:
                    area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                if area < smallest_area:
                    smallest_area = area
                    best_continent = continent_name
            return best_continent
        elif self.game_mode == "world_blocks":
            clicked_blocks = []
            for world_block, bboxes in self.world_blocks_bbox.items():
                for bbox in bboxes:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                        clicked_blocks.append(world_block)
                        break  # Move to the next world block

            if not clicked_blocks:
                return None
            if len(clicked_blocks) == 1:
                return clicked_blocks[0]

            # If the click is in multiple bounding boxes, find the one with the smallest area
            smallest_area = float("inf")
            best_block = None
            for block_name in clicked_blocks:
                area = 0
                for bbox in self.world_blocks_bbox[block_name]:
                    area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                if area < smallest_area:
                    smallest_area = area
                    best_block = block_name
            return best_block
        return None

    def ask_random_item(self):
        if self.game_mode == "countries":
            allowed_countries = [
                "China",
                "Russia",
                "US",
                "Brazil",
                "Egypt",
                "Turkey",
                "Iran",
                "Mexico",
                "Congo (Democratic Republic)",
            ]
            available_countries = [
                country
                for country in self.countries.keys()
                if country in allowed_countries
            ]
            if available_countries:
                self.asked_item = random.choice(available_countries)
            else:
                self.asked_item = None
        elif self.game_mode == "rivers":
            self.asked_item = random.choice(list(self.rivers.keys()))
        elif self.game_mode == "oceans":
            self.asked_item = random.choice(list(self.oceans.keys()))
        elif self.game_mode == "mountains":
            self.asked_item = random.choice(list(self.mountains.keys()))
        elif self.game_mode == "continents":
            self.asked_item = random.choice(list(self.continents.keys()))
        elif self.game_mode == "world_blocks":
            self.asked_item = random.choice(list(self.world_blocks.keys()))
        return self.asked_item

    def get_item_data(self, item_name):
        if self.game_mode == "countries":
            return {"bbox": self.bbox_list.get(item_name)}
        elif self.game_mode == "rivers":
            return self.rivers.get(item_name)
        elif self.game_mode == "oceans":
            return self.oceans.get(item_name)
        elif self.game_mode == "mountains":
            return self.mountains.get(item_name)
        elif self.game_mode == "continents":
            return {"bbox": self.continents_bbox.get(item_name)}
        elif self.game_mode == "world_blocks":
            return {"bbox": self.world_blocks_bbox.get(item_name)}
        return None

    def check_answer(self, item):
        if item == self.asked_item:
            self.score += 1
            return True
        else:
            self.score -= 1
            return False
