from efootprint.abstract_modeling_classes.explainable_objects import ExplainableQuantity
from efootprint.constants.sources import SourceValue, Sources, SourceObject, Source
from efootprint.core.hardware.hardware_base_classes import Hardware
from efootprint.core.usage.user_journey import UserJourney, UserJourneyStep
from efootprint.core.hardware.servers.autoscaling import Autoscaling
from efootprint.core.hardware.storage import Storage
from efootprint.core.service import Service
from efootprint.core.hardware.device_population import DevicePopulation, Devices
from efootprint.core.usage.usage_pattern import UsagePattern
from efootprint.core.hardware.network import Network
from efootprint.core.system import System
from efootprint.constants.countries import Countries
from efootprint.constants.units import u
from efootprint.utils.object_relationships_graphs import build_object_relationships_graph, \
    USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE
from efootprint.utils.plot_emission_diffs import EmissionPlotter
from efootprint.utils.calculus_graph import build_calculus_graph

import os
import matplotlib.pyplot as plt

NB_OF_GPUs = 16
server = Autoscaling(
    "Autoscaling GPU server",
    carbon_footprint_fabrication=SourceValue(600 * NB_OF_GPUs * u.kg, Sources.BASE_ADEME_V19),
    power=SourceValue(300 * NB_OF_GPUs * u.W, Sources.HYPOTHESIS),
    lifespan=SourceValue(6 * u.year, Sources.HYPOTHESIS),
    idle_power=SourceValue(50 * NB_OF_GPUs * u.W, Sources.HYPOTHESIS),
    ram=SourceValue(128 * u.GB, Sources.HYPOTHESIS),
    nb_of_cpus=SourceValue(NB_OF_GPUs * u.core, Sources.HYPOTHESIS),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(300 * u.g / u.kWh, Sources.HYPOTHESIS),
    server_utilization_rate=SourceValue(0.9 * u.dimensionless, Sources.HYPOTHESIS)
)
storage = Storage(
    "SSD storage",
    carbon_footprint_fabrication=SourceValue(160 * u.kg, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power=SourceValue(1.3 * u.W, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    lifespan=SourceValue(6 * u.years, Sources.HYPOTHESIS),
    idle_power=SourceValue(0 * u.W, Sources.HYPOTHESIS),
    storage_capacity=SourceValue(1 * u.TB, Sources.STORAGE_EMBODIED_CARBON_STUDY),
    power_usage_effectiveness=SourceValue(1.2 * u.dimensionless, Sources.HYPOTHESIS),
    average_carbon_intensity=SourceValue(300 * u.g / u.kWh),
    data_replication_factor=SourceValue(3 * u.dimensionless, Sources.HYPOTHESIS),
)
service = Service(
    "ChatGPT serving and training", server, storage, base_ram_consumption=SourceValue(300 * u.MB, Sources.HYPOTHESIS),
    base_cpu_consumption=SourceValue(0 * u.core, Sources.HYPOTHESIS))

chatgpt_training_step = UserJourneyStep(
    "ChatGPT training", service, SourceValue(1 * u.TB / u.uj, Sources.USER_INPUT),
    SourceValue(1 * u.TB / u.uj, Sources.USER_INPUT),
    user_time_spent=SourceValue(24 * u.h / u.uj, Sources.USER_INPUT),
    request_duration=SourceValue(24 * u.h, Sources.HYPOTHESIS),
    cpu_needed=SourceValue(NB_OF_GPUs * u.core / u.uj, Sources.HYPOTHESIS))

training_uj = UserJourney("Training", uj_steps=[chatgpt_training_step])

chatgpt_usage_step = UserJourneyStep(
    "Discussion with chatgpt", service, SourceValue(500 * u.kB / u.uj, Sources.USER_INPUT),
    SourceValue(500 * u.kB / u.uj, Sources.USER_INPUT),
    user_time_spent=SourceValue(5 * u.min / u.uj, Sources.USER_INPUT),
    request_duration=SourceValue(1 * u.min, Sources.HYPOTHESIS),
    cpu_needed=SourceValue(NB_OF_GPUs * u.core / u.uj, Sources.HYPOTHESIS))

discussion_uj = UserJourney("Discussion", uj_steps=[chatgpt_usage_step])

openai_dev = DevicePopulation("OpenAI dev", SourceValue(1 * u.user), Countries.GERMANY, [Devices.LAPTOP])
french_users = DevicePopulation(
    "ChatGPT users in France", SourceValue(1e6 * u.user, Sources.USER_INPUT), Countries.FRANCE, [Devices.LAPTOP])

network = Network("WIFI network", SourceValue(0.05 * u("kWh/GB"), Sources.TRAFICOM_STUDY))


training_up = UsagePattern(
    "Training", training_uj, openai_dev,
    network, SourceValue(90 * u.user_journey / (u.user * u.year), Sources.USER_INPUT),
    SourceObject([[0, 23]]))

usage_up = UsagePattern(
    "Discussions", discussion_uj, french_users,
    network, SourceValue(365 * u.user_journey / (u.user * u.year), Sources.USER_INPUT),
    SourceObject([[9, 23]]))

system = System("ChatGPT training + usage in France", [training_up, usage_up])

print(f"Server carbon footprint is {(server.energy_footprint + server.instances_fabrication_footprint).value}")
print(f"Total system carbon footprint is {system.total_footprint().value}")

object_relationships_graph = build_object_relationships_graph(
    system, classes_to_ignore=USAGE_PATTERN_VIEW_CLASSES_TO_IGNORE)
object_relationships_graph.show(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "object_relationships_graph.html"))

emissions_dict__old = [system.total_energy_footprints(), system.total_fabrication_footprints()]
# video_downloading_step.data_download = SourceValue((2.5 / 12) * u.GB / u.uj, Sources.USER_INPUT)
emissions_dict__new = [system.total_energy_footprints(), system.total_fabrication_footprints()]

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

EmissionPlotter(
    ax, emissions_dict__old, emissions_dict__new, title=system.name, rounding_value=1,
    timespan=ExplainableQuantity(1 * u.year, "one year")).plot_emission_diffs()

plt.show()

graph = build_calculus_graph(system.total_footprint())
graph.show(os.path.join(os.path.abspath(os.path.dirname(__file__)), "full_calculation_graph.html"))