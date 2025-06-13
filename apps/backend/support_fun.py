import json, shutil, requests, h3, os
from os import mkdir
import logging
import pandas as pd
import polars as pl
import numpy as np
from openai import OpenAI
from tqdm import tqdm
from itertools import chain
import xarray as xr
from dask.diagnostics import ProgressBar
from zstandard import ZstdDecompressor
import haversine as hs
from datetime import datetime
import jmespath

from backend import settings

logger = logging.getLogger(__name__)
from backend.raw_backend.support.API_Keys import ApiKeys

file_path_cities = os.path.join(settings.BASE_DIR, 'backend/raw_files', 'worldcitiesh3.parquet')
file_path_airports = os.path.join(settings.BASE_DIR, 'backend/raw_files', 'airports_filtered_h3.parquet')

autocomplete_cities = pl.read_parquet(file_path_cities)
all_airports = pl.read_parquet(file_path_airports)

from concurrent import futures

valid_features_dict = {
    'AIRS': 'a place on a waterbody where floatplanes land and take off',
    'ANCH': 'an area where vessels may anchor',
    'BAY': 'a coastal indentation between two capes or headlands, larger than a cove but smaller than a gulf',
    'BAYS': 'coastal indentations between two capes or headlands, larger than a cove but smaller than a gulf',
    'BGHT': 'an open body of water forming a slight recession in a coastline',
    'BNK': 'an elevation, typically located on a shelf, over which the depth of water is relatively shallow but sufficient for most surface navigation',
    'BNKR': 'a sloping margin of a stream channel which normally confines the stream to its channel on land',
    'BNKX': None,
    'BOG': 'a wetland characterized by peat forming sphagnum moss, sedge, and other acid-water plants',
    'CAPG': 'a dome-shaped mass of glacial ice covering an area of mountain summits or other high lands; smaller than an ice sheet',
    'CHN': 'the deepest part of a stream, bay, lagoon, or strait, through which the main current flows',
    'CHNL': 'that part of a lake having water deep enough for navigation between islands, shoals, etc.',
    'CHNM': 'that part of a body of water deep enough for navigation through an area otherwise not suitable',
    'CHNN': 'a buoyed channel of sufficient depth for the safe navigation of vessels',
    'CNFL': 'a place where two or more streams or intermittent streams flow together',
    'CNL': 'an artificial watercourse',
    'CNLA': 'a conduit used to carry water',
    'CNLB': 'a conspicuously curved or bent section of a canal',
    'CNLD': 'an artificial waterway carrying water away from a wetland or from drainage ditches',
    'CNLI': 'a canal which serves as a main conduit for irrigation water',
    'CNLN': 'a watercourse constructed for navigation of vessels',
    'CNLQ': None,
    'CNLSB': 'a gently inclined underground tunnel bringing water for irrigation from aquifers',
    'CNLX': None,
    'COVE': 'a small coastal indentation, smaller than a bay',
    'CRKT': 'a meandering channel in a coastal wetland subject to bi-directional tidal currents',
    'CRNT': 'a horizontal flow of water in a given direction with uniform velocity',
    'CUTF': 'a channel formed as a result of a stream cutting through a meander neck',
    'DCK': 'a waterway between two piers, or cut into the land for the berthing of ships',
    'DCKB': 'a part of a harbor where ships dock',
    'DOMG': 'a comparatively elevated area on an icecap',
    'DPRG': 'a comparatively depressed area on an icecap',
    'DTCH': 'a small artificial watercourse dug for draining or irrigating the land',
    'DTCHD': 'a ditch which serves to drain the land',
    'DTCHI': 'a ditch which serves to distribute irrigation water',
    'DTCHM': 'an area where a drainage ditch enters a lagoon, lake or bay',
    'ESTY': 'a funnel-shaped stream mouth or embayment where fresh water mixes with sea water under tidal influences',
    'FISH': 'a fishing ground, bank or area where fishermen go to catch fish',
    'FJD': 'a long, narrow, steep-walled, deep-water arm of the sea at high latitudes, usually along mountainous coasts',
    'FJDS': 'long, narrow, steep-walled, deep-water arms of the sea at high latitudes, usually along mountainous coasts',
    'FLLS': 'a perpendicular or very steep descent of the water of a stream',
    'FLLSX': None,
    'FLTM': 'a relatively level area of mud either between high and low tide lines, or subject to flooding',
    'FLTT': 'a large flat area of mud or sand attached to the shore and alternately covered and uncovered by the tide',
    'GLCR': 'a mass of ice, usually at high latitudes or high elevations, with sufficient thickness to flow away from the source area in lobes, tongues, or masses',
    'GULF': 'a large recess in the coastline, larger than a bay',
    'GYSR': 'a type of hot spring with intermittent eruptions of jets of hot water and steam',
    'HBR': 'a haven or space of deep water so sheltered by the adjacent land as to afford a safe anchorage for ships',
    'HBRX': None,
    'INLT': 'a narrow waterway extending into the land, or connecting a bay or lagoon with a larger body of water',
    'INLTQ': 'an inlet which has been filled in, or blocked by deposits',
    'LBED': 'a dried up or drained area of a former lake',
    'LGN': 'a shallow coastal waterbody, completely or partly separated from a larger body of water by a barrier island, coral reef or other depositional feature',
    'LGNS': 'shallow coastal waterbodies, completely or partly separated from a larger body of water by a barrier island, coral reef or other depositional feature',
    'LGNX': None,
    'LK': 'a large inland body of standing water',
    'LKC': 'a lake in a crater or caldera',
    'LKI': None,
    'LKN': 'an inland body of salt water with no outlet',
    'LKNI': None,
    'LKO': 'a crescent-shaped lake commonly found adjacent to meandering streams',
    'LKOI': None,
    'LKS': 'large inland bodies of standing water',
    'LKSB': 'a standing body of water in a cave',
    'LKSC': 'lakes in a crater or caldera',
    'LKSI': None,
    'LKSN': 'inland bodies of salt water with no outlet',
    'LKSNI': None,
    'LKX': None,
    'MFGN': 'diked salt ponds used in the production of solar evaporated salt',
    'MGV': 'a tropical tidal mud flat characterized by mangrove vegetation',
    'MOOR': 'an area of open ground overlaid with wet peaty soils',
    'MRSH': 'a wetland dominated by grass-like vegetation',
    'MRSHN': 'a flat area, subject to periodic salt water inundation, dominated by grassy salt-tolerant plants',
    'NRWS': 'a navigable narrow part of a bay, strait, river, etc.',
    'OCN': 'one of the major divisions of the vast expanse of salt water covering part of the earth',
    'OVF': 'an area of breaking waves caused by the meeting of currents or by waves moving against the current',
    'PND': 'a small standing waterbody',
    'PNDI': None,
    'PNDN': 'a small standing body of salt water often in a marsh or swamp, usually along a seacoast',
    'PNDNI': None,
    'PNDS': 'small standing waterbodies',
    'PNDSF': 'ponds or enclosures in which fish are kept or raised',
    'PNDSI': None,
    'PNDSN': 'small standing bodies of salt water often in a marsh or swamp, usually along a seacoast',
    'POOL': 'a small and comparatively still, deep part of a larger body of water such as a stream or harbor; or a small body of standing water',
    'POOLI': None,
    'RCH': 'a straight section of a navigable stream or channel between two bends',
    'RDGG': 'a linear elevation on an icecap',
    'RDST': 'an open anchorage affording less protection than a harbor',
    'RF': 'a surface-navigation hazard composed of consolidated material',
    'RFC': 'a surface-navigation hazard composed of coral',
    'RFX': None,
    'RPDS': 'a turbulent section of a stream associated with a steep, irregular stream bed',
    'RSV': 'an artificial pond or lake',
    'RSVI': None,
    'RSVT': 'a contained pool or tank of water at, below, or above ground level',
    'RVN': 'a small, narrow, deep, steep-sided stream channel, smaller than a gorge',
    'SBKH': 'a salt flat or salt encrusted plain subject to periodic inundation from flooding or high tides',
    'SD': 'a long arm of the sea forming a channel between the mainland and an island or islands; or connecting two larger bodies of water',
    'SEA': 'a large body of salt water more or less confined by continuous land or chains of islands forming a subdivision of an ocean',
    'SHOL': 'a surface-navigation hazard composed of unconsolidated material',
    'SILL': 'the low part of an underwater gap or saddle separating basins, including a similar feature at the mouth of a fjord',
    'SPNG': 'a place where ground water flows naturally out of the ground',
    'SPNS': 'a place where sulphur ground water flows naturally out of the ground',
    'SPNT': 'a place where hot ground water flows naturally out of the ground',
    'STM': 'a body of running water moving to a lower level in a channel on land',
    'STMA': 'a diverging branch flowing out of a main stream and rejoining it downstream',
    'STMB': 'a conspicuously curved or bent segment of a stream',
    'STMC': 'a stream that has been substantially ditched, diked, or straightened',
    'STMD': 'a branch which flows away from the main stream, as in a delta or irrigation canal',
    'STMH': 'the source and upper part of a stream, including the upper drainage basin',
    'STMI': None,
    'STMIX': None,
    'STMM': 'a place where a stream discharges into a lagoon, lake, or the sea',
    'STMQ': 'a former stream or distributary no longer carrying flowing water, but still evident due to lakes, wetland, topographic or vegetation patterns',
    'STMS': 'bodies of running water moving to a lower level in a channel on land',
    'STMSB': 'a surface stream that disappears into an underground channel, or dries up in an arid area',
    'STMX': None,
    'STRT': 'a relatively narrow waterway, usually narrower and less extensive than a sound, connecting two larger bodies of water',
    'SWMP': 'a wetland dominated by tree vegetation',
    'SYSI': 'a network of ditches and one or more of the following elements: water supply, reservoir, canal, pump, well, drain, etc.',
    'TNLC': 'a tunnel through which a canal passes',
    'WAD': 'a valley or ravine, bounded by relatively steep banks, which in the rainy season becomes a watercourse; found primarily in North Africa and the Middle East',
    'WADB': 'a conspicuously curved or bent segment of a wadi',
    'WADJ': 'a place where two or more wadies join',
    'WADM': 'the lower terminus of a wadi where it widens into an adjoining floodplain, depression, or waterbody',
    'WADS': 'valleys or ravines, bounded by relatively steep banks, which in the rainy season become watercourses; found primarily in North Africa and the Middle East',
    'WADX': None,
    'WHRL': 'a turbulent, rotating movement of water in a stream',
    'WLL': 'a cylindrical hole, pit, or tunnel drilled or dug down to a depth from which water, oil, or gas can be pumped or brought to the surface',
    'WLLQ': None,
    'WLLS': 'cylindrical holes, pits, or tunnels drilled or dug down to a depth from which water, oil, or gas can be pumped or brought to the surface',
    'WTLD': 'an area subject to inundation, usually characterized by bog, marsh, or swamp vegetation',
    'WTLDI': None,
    'WTRC': 'a natural, well-defined channel produced by flowing water, or an artificial channel designed to carry flowing water',
    'WTRH': 'a natural hole, hollow, or small depression that contains water, used by man and animals, especially in arid areas',
    'AGRC': 'a tract of land set aside for agricultural settlement',
    'AMUS': 'Amusement Park are theme parks, adventure parks offering entertainment, similar to funfairs but with a fix location',
    'AREA': 'a tract of land without homogeneous character or boundaries',
    'BSND': 'an area drained by a stream',
    'BSNP': 'an area underlain by an oil-rich structural basin',
    'BTL': 'a site of a land battle of historical importance',
    'CLG': 'an area in a forest with trees removed',
    'CMN': 'a park or pasture for community use',
    'CNS': 'a lease of land by a government for economic development, e.g., mining, forestry',
    'COLF': 'a region in which coal deposits of possible economic value occur',
    'CONT': 'continent: Europe, Africa, Asia, North America, South America, Oceania, Antarctica',
    'CST': 'a zone of variable width straddling the shoreline',
    'CTRB': 'a place where a number of businesses are located',
    'DEVH': 'a tract of land on which many houses of similar design are built according to a development plan',
    'FLD': 'an open as opposed to wooded area',
    'FLDI': 'a tract of level or terraced land which is irrigated',
    'GASF': 'an area containing a subterranean store of natural gas of economic value',
    'GRAZ': 'an area of grasses and shrubs used for grazing',
    'GVL': 'an area covered with gravel',
    'INDS': 'an area characterized by industrial activity',
    'LAND': 'a tract of land in the Arctic',
    'LCTY': 'a minor area or place of unspecified or mixed character and indefinite boundaries',
    'MILB': 'a place used by an army or other armed service for storing arms and supplies, and for accommodating and training troops, a base from which operations can be initiated',
    'MNA': 'an area of mine sites where minerals and ores are extracted',
    'MVA': 'a tract of land where military field exercises are carried out',
    'NVB': 'an area used to store supplies, provide barracks for troops and naval personnel, a port for naval vessels, and from which operations are initiated',
    'OAS': 'an area in a desert made productive by the availability of water',
    'OILF': 'an area containing a subterranean store of petroleum of economic value',
    'PEAT': 'an area where peat is harvested',
    'PRK': 'an area, often of forested land, maintained as a place of beauty, or for recreation',
    'PRT': 'a place provided with terminal and transfer facilities for loading and discharging waterborne cargo or passengers, usually located in a harbor',
    'QCKS': 'an area where loose sand with water moving through it may become unstable when heavy objects are placed at the surface, causing them to sink',
    'RES': 'a tract of public land reserved for future use or restricted as to use',
    'RESA': 'a tract of land reserved for agricultural reclamation and/or development',
    'RESF': 'a forested area set aside for preservation or controlled use',
    'RESH': 'a tract of land used primarily for hunting',
    'RESN': 'an area reserved for the maintenance of a natural habitat',
    'RESP': 'an area of palm trees where use is controlled',
    'RESV': 'a tract of land set aside for aboriginal, tribal, or native populations',
    'RESW': 'a tract of public land reserved for the preservation of wildlife',
    'RGNE': 'a region of a country established for economic development or for statistical purposes',
    'RGNH': 'a former historic area distinguished by one or more observable physical or cultural characteristics',
    'RGNL': 'a tract of land distinguished by numerous lakes',
    'RNGA': 'a tract of land used for artillery firing practice',
    'SALT': 'a shallow basin or flat where salt accumulates after periodic inundation',
    'SNOW': 'an area of permanent snow and ice forming the accumulation area of a glacier',
    'TRB': 'a tract of land used by nomadic or other tribes',
    'APNU': 'a gentle slope, with a generally smooth surface, particularly found around groups of islands and seamounts',
    'ARCU': 'a low bulge around the southeastern end of the island of Hawaii',
    'ARRU': 'an area of subdued corrugations off Baja California',
    'BDLU': 'a region adjacent to a continent, normally occupied by or bordering a shelf, that is highly irregular with depths well in excess of those typical of a shelf',
    'BKSU': 'elevations, typically located on a shelf, over which the depth of water is relatively shallow but sufficient for safe surface navigation',
    'BNKU': 'an elevation, typically located on a shelf, over which the depth of water is relatively shallow but sufficient for safe surface navigation',
    'BSNU': 'a depression more or less equidimensional in plan and of variable extent',
    'CDAU': 'an entire mountain system including the subordinate ranges, interior plateaus, and basins',
    'CNSU': 'relatively narrow, deep depressions with steep sides, the bottom of which generally has a continuous slope',
    'CNYU': 'a relatively narrow, deep depression with steep sides, the bottom of which generally has a continuous slope',
    'CRSU': 'a gentle slope rising from oceanic depths towards the foot of a continental slope',
    'DEPU': 'a localized deep area within the confines of a larger feature, such as a trough, basin or trench',
    'EDGU': 'a line along which there is a marked increase of slope at the outer margin of a continental shelf or island shelf',
    'ESCU': 'an elongated and comparatively steep slope separating flat or gently sloping areas',
    'FANU': 'a relatively smooth feature normally sloping away from the lower termination of a canyon or canyon system',
    'FLTU': 'a small level or nearly level area',
    'FRZU': 'an extensive linear zone of irregular topography of the sea floor, characterized by steep-sided or asymmetrical ridges, troughs, or escarpments',
    'FURU': 'a closed, linear, narrow, shallow depression',
    'GAPU': 'a narrow break in a ridge or rise',
    'GLYU': 'a small valley-like feature',
    'HLLU': 'an elevation rising generally less than 500 meters',
    'HLSU': 'elevations rising generally less than 500 meters',
    'HOLU': 'a small depression of the sea floor',
    'KNLU': 'an elevation rising generally more than 500 meters and less than 1,000 meters and of limited extent across the summit',
    'KNSU': 'elevations rising generally more than 500 meters and less than 1,000 meters and of limited extent across the summits',
    'LDGU': 'a rocky projection or outcrop, commonly linear and near shore',
    'LEVU': 'an embankment bordering a canyon, valley, or seachannel',
    'MESU': 'an isolated, extensive, flat-topped elevation on the shelf, with relatively steep sides',
    'MNDU': 'a low, isolated, rounded hill',
    'MOTU': 'an annular depression that may not be continuous, located at the base of many seamounts, islands, and other isolated elevations',
    'MTU': 'a well-delineated subdivision of a large and complex positive feature',
    'PKSU': 'prominent elevations, part of a larger feature, either pointed or of very limited extent across the summit',
    'PKU': 'a prominent elevation, part of a larger feature, either pointed or of very limited extent across the summit',
    'PLNU': 'a flat, gently sloping or nearly level region',
    'PLTU': 'a comparatively flat-topped feature of considerable extent, dropping off abruptly on one or more sides',
    'PNLU': 'a high tower or spire-shaped pillar of rock or coral, alone or cresting a summit',
    'PRVU': 'a region identifiable by a group of similar physiographic features whose characteristics are markedly in contrast with surrounding areas',
    'RDGU': 'a long narrow elevation with steep sides',
    'RDSU': 'long narrow elevations with steep sides',
    'RFSU': 'surface-navigation hazards composed of consolidated material',
    'RFU': 'a surface-navigation hazard composed of consolidated material',
    'RISU': 'a broad elevation that rises gently, and generally smoothly, from the sea floor',
    'SCNU': 'a continuously sloping, elongated depression commonly found in fans or plains and customarily bordered by levees on one or two sides',
    'SCSU': 'continuously sloping, elongated depressions commonly found in fans or plains and customarily bordered by levees on one or two sides',
    'SDLU': 'a low part, resembling in shape a saddle, in a ridge or between contiguous seamounts',
    'SHFU': 'a zone adjacent to a continent (or around an island) that extends from the low water line to a depth at which there is usually a marked increase of slope towards oceanic depths',
    'SHLU': 'a surface-navigation hazard composed of unconsolidated material',
    'SHSU': 'hazards to surface navigation composed of unconsolidated material',
    'SHVU': 'a valley on the shelf, generally the shoreward extension of a canyon',
    'SILU': 'the low part of a gap or saddle separating basins',
    'SLPU': 'the slope seaward from the shelf edge to the beginning of a continental rise or the point where there is a general reduction in slope',
    'SMSU': 'elevations rising generally more than 1,000 meters and of limited extent across the summit',
    'SMU': 'an elevation rising generally more than 1,000 meters and of limited extent across the summit',
    'SPRU': 'a subordinate elevation, ridge, or rise projecting outward from a larger feature',
    'TERU': 'a relatively flat horizontal or gently inclined surface, sometimes long and narrow, which is bounded by a steeper ascending slope on one side and by a steep descending slope on the opposite side',
    'TMSU': 'seamounts having a comparatively smooth, flat top',
    'TMTU': 'a seamount having a comparatively smooth, flat top',
    'TNGU': 'an elongate (tongue-like) extension of a flat sea floor into an adjacent higher feature',
    'TRGU': 'a long depression of the sea floor characteristically flat bottomed and steep sided, and normally shallower than a trench',
    'TRNU': 'a long, narrow, characteristically very deep and asymmetrical depression of the sea floor, with relatively steep sides',
    'VALU': 'a relatively shallow, wide depression, the bottom of which usually has a continuous gradient',
    'VLSU': 'a relatively shallow, wide depression, the bottom of which usually has a continuous gradient',
    'BUSH': 'a small clump of conspicuous bushes in an otherwise bare area',
    'CULT': 'an area under cultivation',
    'FRST': 'an area dominated by tree vegetation',
    'FRSTF': "a forest fossilized by geologic processes and now exposed at the earth's surface",
    'GROVE': 'a small wooded area or collection of trees growing closely together, occurring naturally or deliberately planted',
    'GRSLD': 'an area dominated by grass vegetation',
    'GRVC': 'a planting of coconut trees',
    'GRVO': 'a planting of olive trees',
    'GRVP': 'a planting of palm trees',
    'GRVPN': 'a planting of pine trees',
    'HTH': 'an upland moor or sandy area dominated by low shrubby vegetation including heather',
    'MDW': 'a small, poorly drained area dominated by grassy vegetation',
    'OCH': 'a planting of fruit or nut trees',
    'SCRB': 'an area of low trees, bushes, and shrubs stunted by some environmental limitation',
    'TREE': 'a conspicuous tree used as a landmark',
    'TUND': 'a marshy, treeless, high latitude plain, dominated by mosses, lichens, and low shrub vegetation under permafrost conditions',
    'VIN': 'a planting of grapevines',
    'VINS': 'plantings of grapevines',
    'null': None,
    'TRL': 'a path, track, or route used by pedestrians, animals, or off-road vehicles',
    'ANS': 'a place where archeological remains, old structures, or cultural artifacts are located',
    'ART': 'a piece of art, like a sculpture, painting. In contrast to monument (MNMT) it is not commemorative.',
    'ATHF': 'a tract of land used for playing team sports, and athletic track and field events',
    'CAVE': 'an underground passageway or chamber, or cavity on the side of a cliff',
    'CH': 'a building for public Christian worship',
    'CMP': 'a site occupied by tents, huts, or other shelters for temporary use',
    'CSNO': 'a building used for entertainment, especially gambling',
    'CSTL': 'a large fortified building or set of buildings',
    'CTRR': 'a facility where more than one religious activity is carried out, e.g., retreat, school, monastery, worship',
    'CTRS': 'a facility for launching, tracking, or controlling satellites and space vehicles',
    'FT': 'a defensive structure or earthworks',
    'FY': 'a boat or other floating conveyance and terminal facilities regularly used to transport people and vehicles across a waterbody',
    'FYT': 'a place where ferries pick-up and discharge passengers, vehicles and or cargo',
    'GDN': 'an enclosure for displaying selected plant or animal life',
    'HSP': 'a building in which sick or injured, especially those confined to bed, are medically treated',
    'HSPC': 'a medical facility associated with a hospital for outpatients',
    'HSTS': 'a place of historical importance',
    'LTHSE': 'a distinctive structure exhibiting a major navigation light',
    'MALL': 'A large, often enclosed shopping complex containing various stores, businesses, and restaurants usually accessible by common passageways.',
    'MAR': 'a harbor facility for small boats, yachts, etc.',
    'MFGB': 'one or more buildings where beer is brewed',
    'MLWTR': 'a mill powered by running water',
    'MNMT': 'a commemorative structure or statue',
    'MSQE': 'a building for public Islamic worship',
    'MSTY': 'a building and grounds where a community of monks lives in seclusion',
    'MUS': 'a building where objects of permanent interest in one or more of the arts and sciences are preserved and exhibited',
    'OBPT': 'a wildlife or scenic observation point',
    'OPRA': 'A theater designed chiefly for the performance of operas.',
    'PAL': 'a large stately house, often a royal or presidential residence',
    'PYR': 'an ancient massive structure of square ground plan with four triangular faces meeting at a point and used for enclosing tombs',
    'PYRS': 'ancient massive structures of square ground plan with four triangular faces meeting at a point and used for enclosing tombs',
    'RECG': 'a recreation field where golf is played',
    'RECR': 'a track where races are held',
    'REST': 'A place where meals are served to the public',
    'RLG': 'an ancient site of significant religious importance',
    'RSRT': 'a specialized facility for vacation, health, or participation sports activities',
    'RUIN': 'a destroyed or decayed structure which is no longer functional',
    'SHRN': 'a structure or place memorializing a person or religious concept',
    'SPA': 'a resort area usually developed around a medicinal spring',
    'SQR': 'a broad, open, public area near the center of a town or city',
    'STDM': 'a structure with an enclosure for athletic games with tiers of seats for spectators',
    'SYG': 'a place for Jewish worship and religious instruction',
    'THTR': 'a building or outdoor area used for live theatrical presentations, concerts, opera or dance productions, cinema, and/or other stage productions',
    'TMB': 'a structure for interring bodies',
    'TMPL': 'an edifice dedicated to religious worship',
    'WALLA': 'the remains of a linear defensive stone structure',
    'WRCK': 'the site of the remains of a wrecked vessel',
    'ZOO': 'a zoological garden or park where wild animals are kept for exhibition',
    'ATOL': 'a ring-shaped coral reef which has closely spaced islands on it encircling a lagoon',
    'BAR': 'a shallow ridge or mound of coarse unconsolidated material in a stream channel, at the mouth of a stream, estuary, or lagoon and in the wave-break zone along coasts',
    'BCH': 'a shore zone of coarse unconsolidated sediment that extends from the low-water line to the highest reach of storm waves',
    'BCHS': 'a shore zone of coarse unconsolidated sediment that extends from the low-water line to the highest reach of storm waves',
    'BDLD': 'an area characterized by a maze of very closely spaced, deep, narrow, steep-sided ravines, and sharp crests and pinnacles',
    'BLHL': 'a hole in coastal rock through which sea water is forced by a rising tide or waves and spurted through an outlet into the air',
    'BNCH': 'a long, narrow bedrock platform bounded by steeper slopes above and below, usually overlooking a waterbody',
    'BUTE': 'a small, isolated, usually flat-topped hill with steep sides',
    'CAPE': 'a land area, more prominent than a point, projecting into the sea and marking a notable change in coastal direction',
    'CFT': 'a deep narrow slot, notch, or groove in a coastal cliff',
    'CLDA': 'a depression measuring kilometers across formed by the collapse of a volcanic mountain',
    'CLF': 'a high, steep to perpendicular slope overlooking a waterbody or lower area',
    'CNYN': 'a deep, narrow valley with steep sides cutting into a plateau or mountainous area',
    'CONE': 'a conical landform composed of mud or volcanic material',
    'CRQ': 'a bowl-like hollow partially surrounded by cliffs or steep slopes at the head of a glaciated valley',
    'CRQS': 'bowl-like hollows partially surrounded by cliffs or steep slopes at the head of a glaciated valley',
    'CRTR': 'a generally circular saucer or bowl-shaped depression caused by volcanic or meteorite explosive action',
    'DLTA': 'a flat plain formed by alluvial deposits at the mouth of a stream',
    'DPR': 'a low area surrounded by higher land and usually characterized by interior drainage',
    'DSRT': 'a large area with little or no vegetation due to extreme environmental conditions',
    'DUNE': 'a wave form, ridge or star shape feature composed of sand',
    'ERG': 'an extensive tract of shifting sand and sand dunes',
    'FAN': 'a fan-shaped wedge of coarse alluvium with apex merging with a mountain stream bed and the fan spreading out at a low angle slope onto an adjacent plain',
    'FORD': 'a shallow part of a stream which can be crossed on foot or by land vehicle',
    'FSR': 'a crack associated with volcanism',
    'GRGE': 'a short, narrow, steep-sided section of a stream valley',
    'HDLD': 'a high projection of land extending into a large body of water beyond the line of the coast',
    'HLL': 'a rounded elevation of limited extent rising above the surrounding land with local relief of less than 300m',
    'HLLS': 'rounded elevations of limited extent rising above the surrounding land with local relief of less than 300m',
    'HMCK': 'a patch of ground, distinct from and slightly above the surrounding plain or wetland. Often occurs in groups',
    'HMDA': 'a relatively sand-free, high bedrock plateau in a hot desert, with or without a gravel veneer',
    'ISL': 'a tract of land, smaller than a continent, surrounded by water at high water',
    'ISLET': 'small island, bigger than rock, smaller than island.',
    'ISLF': 'an island created by landfill or diking and filling in a wetland, bay, or lagoon',
    'ISLM': 'a mangrove swamp surrounded by a waterbody',
    'ISLS': 'tracts of land, smaller than a continent, surrounded by water at high water',
    'ISLT': 'a coastal island connected to the mainland by barrier beaches, levees or dikes',
    'ISLX': None,
    'ISTH': 'a narrow strip of land connecting two larger land masses and bordered by water',
    'KRST': 'a distinctive landscape developed on soluble rock such as limestone characterized by sinkholes, caves, disappearing streams, and underground drainage',
    'LAVA': 'an area of solidified lava',
    'LEV': 'a natural low embankment bordering a distributary or meandering stream; often built up artificially to control floods',
    'MESA': 'a flat-topped, isolated elevation with steep slopes on all sides, less extensive than a plateau',
    'MND': 'a low, isolated, rounded hill',
    'MRN': 'a mound, ridge, or other accumulation of glacial till',
    'MT': 'an elevation standing high above the surrounding area with small summit area, steep slopes and local relief of 300m or more',
    'MTS': 'a mountain range or a group of mountains or high ridges',
    'NKM': 'a narrow strip of land between the two limbs of a meander loop at its narrowest point',
    'NTKS': 'rocks or mountain peaks protruding through glacial ice',
    'PAN': 'a near-level shallow, natural depression or basin, usually containing an intermittent lake, pond, or pool',
    'PANS': 'a near-level shallow, natural depression or basin, usually containing an intermittent lake, pond, or pool',
    'PASS': 'a break in a mountain range or other high obstruction, used for transportation from one side to the other [See also gap]',
    'PEN': 'an elongate area of land projecting into a body of water and nearly surrounded by water',
    'PENX': None,
    'PK': 'a pointed elevation atop a mountain, ridge, or other hypsographic feature',
    'PKS': 'pointed elevations atop a mountain, ridge, or other hypsographic features',
    'PLAT': 'an elevated plain with steep slopes on one or more sides, and often with incised streams',
    'PLATX': None,
    'PLDR': 'an area reclaimed from the sea by diking and draining',
    'PLN': 'an extensive area of comparatively level to gently undulating land, lacking surface irregularities, and usually adjacent to a higher area',
    'PLNX': None,
    'PROM': 'a bluff or prominent hill overlooking or projecting into a lowland',
    'PT': 'a tapering piece of land projecting into a body of water, less prominent than a cape',
    'PTS': 'tapering pieces of land projecting into a body of water, less prominent than a cape',
    'RDGB': 'a ridge of sand just inland and parallel to the beach, usually in series',
    'RDGE': 'a long narrow elevation with steep sides, and a more or less continuous crest',
    'REG': 'a desert plain characterized by a surface veneer of gravel and stones',
    'SAND': 'a tract of land covered with sand',
    'SCRP': 'a long line of cliffs or steep slopes separating level surfaces above and below',
    'SDL': 'a broad, open pass crossing a ridge or between hills or mountains',
    'SHOR': 'a narrow zone bordering a waterbody which covers and uncovers at high and low water, respectively',
    'SINK': 'a small crater-shape depression in a karst area',
    'SLID': 'a mound of earth material, at the base of a slope and the associated scoured area',
    'SLP': 'a surface with a relatively uniform slope angle',
    'SPIT': 'a narrow, straight or curved continuation of a beach into a waterbody',
    'SPUR': 'a subordinate ridge projecting outward from a hill, mountain or other elevation',
    'TAL': 'a steep concave slope formed by an accumulation of loose rock fragments at the base of a cliff or steep slope',
    'TRGD': 'a long wind-swept trough between parallel longitudinal dunes',
    'TRR': 'a long, narrow alluvial platform bounded by steeper slopes above and below, usually overlooking a waterbody',
    'UPLD': 'an extensive interior region of high land with low to moderate surface relief',
    'VAL': 'an elongated depression usually traversed by a stream',
    'VALG': 'a valley the floor of which is notably higher than the valley or shore to which it leads; most common in areas that have been glaciated',
    'VALS': 'elongated depressions usually traversed by a stream',
    'VALX': None}
feature_codes = list(valid_features_dict.keys())


def get_hotels_file(rh_key, rh_secret):
    url = "https://api.worldota.net/api/b2b/v3/hotel/info/dump/"
    payload = json.dumps({
        "inventory": "all",
        "language": "en"
    })

    headers = {
        'Content-Type': 'application/json'
    }
    auth = (rh_secret, rh_key)

    response = requests.request("POST", url, headers=headers, data=payload, auth=auth).json()

    return response


def extract_hotel_data(filename: str):
    """
    Extract specific information from all hotels in a .zstd compressed file.
    :param filename: path to a zstd archive
    :return: List of dictionaries with extracted hotel data
    """
    hotels = []

    with open(filename, "rb") as fh:
        # Make decompressor
        dctx = ZstdDecompressor()
        with dctx.stream_reader(fh) as reader:
            previous_line = ""
            while True:
                # Read the file by 16 MB chunk
                chunk = reader.read(2 ** 24)
                if not chunk:
                    break

                try:
                    # Decode with error handling to skip problematic characters
                    raw_data = chunk.decode("utf-8", errors="replace")
                except UnicodeDecodeError as e:
                    print(f"Unicode decode error: {e}")
                    continue

                # Split by new line character
                lines = raw_data.split("\n")
                for i, line in enumerate(lines[:-1]):
                    if i == 0:
                        line = previous_line + line
                    try:
                        hotel_data = json.loads(line)
                        # Extract desired information
                        extracted_data = {
                            'id': hotel_data['id'],
                            'latitude': hotel_data['latitude'],
                            'longitude': hotel_data['longitude'],
                            'star_rating': hotel_data.get('star_rating'),  # Use get() to avoid KeyError
                            'type': hotel_data['kind'],
                            'country_code': hotel_data['region']['country_code']
                        }
                        hotels.append(extracted_data)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
                    except KeyError as e:
                        # Log missing keys (optional)
                        print(f"Missing key {e} in hotel data: {line}")
                        continue
                # Save the last line to concatenate with the next chunk
                previous_line = lines[-1]

    return hotels


def get_geonames_parquet(path_to_csv):
    schema = {
        "geonameid": pl.Int64,
        "name": pl.Utf8,
        "asciiname": pl.Utf8,
        "alternatenames": pl.Utf8,
        "latitude": pl.Float64,
        "longitude": pl.Float64,
        "feature_class": pl.Utf8,
        "feature_code": pl.Utf8,
        "country_code": pl.Utf8,
        "cc2_code": pl.Utf8,
        "admin1_code": pl.Utf8,
        "admin2_code": pl.Utf8,
        "admin3_code": pl.Utf8,
        "admin4_code": pl.Utf8,
        "population": pl.Utf8,  # Load as Utf8 for now
        "elevation": pl.Float64,
        "dem": pl.Int64,
        "timezone": pl.Utf8,
        "modification_date": pl.Utf8,  # Load as Utf8 for now
    }

    df = pl.read_csv(
        path_to_csv,
        separator="\t",
        schema=schema,
        null_values="",  # Handle empty values
        ignore_errors=True  # Skip problematic rows for now
    )

    # Clean up the population column
    df = df.with_columns(
        pl.col("population")
        .str.strip_chars()  # Remove whitespace
        .str.replace_all(r"[^0-9]", "")  # Remove non-numeric characters
        .cast(pl.Int64, strict=False)  # Convert to Int64, allowing nulls
    )

    df = df.with_columns(
        pl.col("modification_date")
        .cast(pl.Utf8)  # Ensure the column is a string
        .str.strip_chars()  # Remove any whitespace
        .str.strptime(pl.Date, format="%Y-%m-%d", strict=False)  # Parse to Date
    )

    result = df.select(['geonameid',
                        'name',
                        'asciiname',
                        'alternatenames',
                        'latitude',
                        'longitude',
                        'feature_class',
                        'feature_code',
                        'country_code',
                        'population',
                        'elevation',
                        ])

    result.write_parquet('geonames.parquet')


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(lat2), np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


#  add h3 indexes to dataset based on lat, lon
def add_h3_index(df, lat_col="latitude", lon_col="longitude", resolutions=(0, 1, 2, 3, 4, 5, 6, 7)):
    """
    Adds an H3 index column to a DataFrame based on latitude and longitude columns.
    """
    for resolution in tqdm(resolutions, unit="index", desc="Adding H3 index"):
        df[f"h3_index_{resolution}"] = df.apply(lambda row: h3.latlng_to_cell(row[lat_col], row[lon_col], resolution),
                                                axis=1)

    return df


#  Filter first/second order cities and return most populated places in radius area
def cities_filter(df, h3_resolution, h3_radius):
    indexes = set(df[f'h3_index_{h3_resolution}'].to_list())
    indexes_with_radius = [h3.grid_disk(index, h3_radius) for index in indexes]

    all = []
    for i in indexes_with_radius:
        cluster = df.filter(pl.col(f'h3_index_{h3_resolution}').is_in(i))
        prime_in_cluster = cluster.sort(by='population', descending=True).head(1)
        all.append(prime_in_cluster)

    result = pl.concat(all, how='vertical').unique()

    return result


#  Iterate in cycles on dataset to clean important area of all 'unimportant' populated places (e.g. kill districts inside New York city)
def filter_until_stable(df, h3_resolution, h3_radius):
    # Initial setup
    previous_height = df.height
    current_df = cities_filter(df=df, h3_resolution=h3_resolution, h3_radius=h3_radius)
    step = 1

    # Loop until the height stabilizes
    while current_df.height != previous_height:
        previous_height = current_df.height
        current_df = cities_filter(df=current_df, h3_resolution=h3_resolution, h3_radius=h3_radius)
        step += 1
        # print(f"Iteration {step}: Height = {current_df.height}")

    return current_df  # Return the DataFrame when height stabilizes


#  Returns filtered dataset
def filtered_cities_h3(cities_df, h3_resolution, foc_radius, soc_radius, min_pop=200, foc_min_pop=30000):
    foc = cities_df.filter(
        ((pl.col('feature_code').is_in(['PPLC', 'PPLA'])) & (pl.col('population') > min_pop)) |
        ((pl.col('feature_code').is_in(['PPL', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLA5'])) & (
                pl.col('population') > foc_min_pop))
    )

    foc_indexes = set(foc[f'h3_index_{h3_resolution}'].to_list())
    foc_indexes_with_radius = [h3.grid_disk(index, foc_radius) for index in foc_indexes]

    try:
        all_indexes = list(set(np.array(foc_indexes_with_radius).flatten()))
    except:
        all_indexes = list(set(list(chain.from_iterable(foc_indexes_with_radius))))
    # all_indexes = list(set(np.array(foc_indexes_with_radius).flatten()))

    soc = cities_df.filter((~pl.col(f'h3_index_{h3_resolution}').is_in(all_indexes)) & (pl.col('population') > min_pop))
    try:
        foc_filtered = filter_until_stable(df=foc, h3_resolution=h3_resolution, h3_radius=foc_radius)
    except:
        foc_filtered = foc
    try:
        soc_filtered = filter_until_stable(df=soc, h3_resolution=h3_resolution, h3_radius=soc_radius)
        result = pl.concat([foc_filtered, soc_filtered])
    except:
        result = foc_filtered

    return result


#  Struct data from geonames
def make_raw_data(airports_df, cities_df, features_df, hotels_df, countries_metadata, raw_data_dir):
    shutil.rmtree(raw_data_dir)
    os.mkdir(raw_data_dir)
    list_of_valid_country_codes = countries_metadata['country_code'].to_list()

    for country_code in list_of_valid_country_codes:
        os.mkdir(f'{raw_data_dir}/{country_code}')

        airports = airports_df.filter(pl.col('country_code') == country_code)
        airports.write_parquet(f'{raw_data_dir}/{country_code}/airports_raw.parquet')

        cities = cities_df.filter(pl.col('country_code') == country_code)
        cities.write_parquet(f'{raw_data_dir}/{country_code}/cities_raw.parquet')

        features = features_df.filter(pl.col('country_code') == country_code)
        features.write_parquet(f'{raw_data_dir}/{country_code}/features_raw.parquet')

        hotels = hotels_df.filter(pl.col('country_code') == country_code)
        hotels.write_parquet(f'{raw_data_dir}/{country_code}/hotels_raw.parquet')


#  Returns dir with h3 mapped data
def make_h3_data(raw_data_dir, h3_data_dir):
    list_of_countries = ['IS',
                         'EE',
                         'EC',
                         'YT',
                         'GN',
                         'SE',
                         'GD',
                         'BB',
                         'KH',
                         'NC',
                         'SO',
                         'ZA',
                         'AQ',
                         'BM',
                         'SZ',
                         'HT',
                         'LC',
                         'AZ',
                         'RW',
                         'PK',
                         'MS',
                         'PA',
                         'FO',
                         'PG',
                         'NG',
                         'DJ',
                         'FM',
                         'KE',
                         'MM',
                         'PF',
                         'CO',
                         'WS',
                         'AS',
                         'SY',
                         'SK',
                         'PT',
                         'DE',
                         'CC',
                         'CK',
                         'PL',
                         'CU',
                         'KR',
                         'VC',
                         'PM',
                         'ZM',
                         'DM',
                         'LK',
                         'BR',
                         'FJ',
                         'SV',
                         'SB',
                         'GH',
                         'DK',
                         'MP',
                         'CL',
                         'PE',
                         'MA',
                         'AX',
                         'IM',
                         'MX',
                         'MQ',
                         'CM',
                         'UG',
                         'TG',
                         'FR',
                         'MN',
                         'CI',
                         'SC',
                         'JP',
                         'CX',
                         'CA',
                         'BT',
                         'CR',
                         'BS',
                         'PS',
                         'LU',
                         'AG',
                         'ET',
                         'GR',
                         'MY',
                         'BY',
                         'IN',
                         'VE',
                         'TT',
                         'AM',
                         'BO',
                         'DZ',
                         'RE',
                         'GT',
                         'RO',
                         'ID',
                         'AI',
                         'EH',
                         'OM',
                         'NF',
                         'IR',
                         'AL',
                         'KY',
                         'TR',
                         'BG',
                         'JE',
                         'AF',
                         'GG',
                         'CN',
                         'FK',
                         'CF',
                         'AD',
                         'BH',
                         'LR',
                         'TD',
                         'IL',
                         'HM',
                         'TJ',
                         'PN',
                         'SM',
                         'GS',
                         'VN',
                         'SJ',
                         'GM',
                         'BL',
                         'CZ',
                         'BD',
                         'TV',
                         'YE',
                         'MU',
                         'MF',
                         'CG',
                         'GI',
                         'TH',
                         'MG',
                         'MK',
                         'MC',
                         'KI',
                         'NE',
                         'KZ',
                         'IQ',
                         'AR',
                         'SR',
                         'CW',
                         'VU',
                         'KN',
                         'GW',
                         'GY',
                         'PH',
                         'KP',
                         'ST',
                         'NU',
                         'TW',
                         'GA',
                         'GE',
                         'LA',
                         'CH',
                         'MD',
                         'SL',
                         'HU',
                         'US',
                         'PR',
                         'AO',
                         'BJ',
                         'NZ',
                         'KM',
                         'RU',
                         'UY',
                         'PW',
                         'VI',
                         'TN',
                         'HN',
                         'IE',
                         'SH',
                         'NI',
                         'BA',
                         'IO',
                         'BZ',
                         'TL',
                         'YU',
                         'BN',
                         'GF',
                         'TC',
                         'BI',
                         'HR',
                         'DO',
                         'KG',
                         'KW',
                         'MZ',
                         'GL',
                         'MO',
                         'ME',
                         'XK',
                         'GU',
                         'GQ',
                         'LI',
                         'RS',
                         'CD',
                         'BW',
                         'NP',
                         'MH',
                         'FI',
                         'ES',
                         'JO',
                         'BV',
                         'AU',
                         'BQ',
                         'UM',
                         'AN',
                         'NA',
                         'LS',
                         'SD',
                         'IT',
                         'BF',
                         'EG',
                         'ER',
                         'TM',
                         'VG',
                         'SS',
                         'MV',
                         'GP',
                         'LT',
                         'CS',
                         'HK',
                         'SX',
                         'MW',
                         'NR',
                         'NO',
                         'QA',
                         'SG',
                         'LY',
                         'CV',
                         'MR',
                         'LV',
                         'JM',
                         'VA',
                         'MT',
                         'SN',
                         'LB',
                         'TK',
                         'AE',
                         'ZW',
                         'TF',
                         'NL',
                         'AW',
                         'TZ',
                         'CY',
                         'AT',
                         'PY',
                         'SA',
                         'UZ',
                         'GB',
                         'UA',
                         'ML',
                         'TO',
                         'SI',
                         'WF',
                         'BE']
    processed = []
    with_issue = []
    shutil.rmtree(h3_data_dir)
    os.mkdir(h3_data_dir)
    for index, country in enumerate(list_of_countries):

        try:
            airports = pl.read_parquet(f'{raw_data_dir}/{country}/airports_raw.parquet').to_pandas()
            cities = pl.read_parquet(f'{raw_data_dir}/{country}/cities_raw.parquet').to_pandas()
            hotels = pl.read_parquet(f'{raw_data_dir}/{country}/hotels_raw.parquet').to_pandas()
            features = pl.read_parquet(f'{raw_data_dir}/{country}/features_raw.parquet').to_pandas()

            airports_h3 = add_h3_index(df=airports)
            cities_h3 = add_h3_index(df=cities)
            hotels_h3 = add_h3_index(df=hotels)
            features_h3 = add_h3_index(df=features)
            os.mkdir(f'{h3_data_dir}/{country}')

            airports_h3.to_parquet(f'{h3_data_dir}/{country}/airports_h3.parquet')
            cities_h3.to_parquet(f'{h3_data_dir}/{country}/cities_h3.parquet')
            hotels_h3.to_parquet(f'{h3_data_dir}/{country}/hotels_h3.parquet')
            features_h3.to_parquet(f'{h3_data_dir}/{country}/features_h3.parquet')
            processed.append(country)

        except:

            with_issue.append(country)


#  Data preparation for filtering
def valid_cities_mapping(countries_metadata, h3_data_dir):
    list_of_valid_country_codes = countries_metadata['country_code'].to_list()

    resolution = []
    foc_radius = []
    soc_radius = []
    for i in list_of_valid_country_codes:
        all_populated_places = pl.read_parquet(f'{h3_data_dir}/{i}/cities_h3.parquet')
        biggest_city = all_populated_places.sort(by='population', descending=True).head(1)['population'].item()
        number_of_big_cities = countries_metadata.filter(pl.col('number_of_big_cities') > 0).height

        #  Logic for cities mapping (default: based on biggest city size and number of 'big' cities)

        if biggest_city > 3000000 and number_of_big_cities > 1:
            resolution.append(6)
            foc_radius.append(6)
            soc_radius.append(2)
        elif 3000000 > biggest_city > 1500000:
            resolution.append(6)
            foc_radius.append(4)
            soc_radius.append(2)
        elif 1500000 > biggest_city > 500000:
            resolution.append(6)
            foc_radius.append(3)
            soc_radius.append(1)
        else:
            resolution.append(7)
            foc_radius.append(2)
            soc_radius.append(1)

    countries_metadata = countries_metadata.with_columns(pl.Series(name="resolution", values=resolution))
    countries_metadata = countries_metadata.with_columns(pl.Series(name="foc_radius", values=foc_radius))
    countries_metadata = countries_metadata.with_columns(pl.Series(name="soc_radius", values=soc_radius))

    return countries_metadata


def filter_by_hotels(dataset, hotels, h3_params):
    central_cells_h3_indexes = dataset[f'h3_index_{h3_params[0]}'].to_list()
    widen_cells_h3_indexes = [h3.grid_disk(cell, h3_params[1]) for cell in central_cells_h3_indexes]
    #
    # try:
    #     valid_indexes = list(set(np.array(widen_cells_h3_indexes).flatten()))
    # except:
    #     valid_indexes = list(set(list(chain.from_iterable(widen_cells_h3_indexes))))

    hotels_num = [hotels.filter(pl.col(f'h3_index_{h3_params[0]}').is_in(cluster)).height for cluster in
                  widen_cells_h3_indexes]
    hotels_num5 = [hotels.filter((pl.col(f'h3_index_{h3_params[0]}').is_in(cluster)) & (
        pl.col('star_rating').is_in([4, 5]))).height for cluster in widen_cells_h3_indexes]
    dataset = dataset.with_columns([
        pl.Series("number_of_hotels", hotels_num),
        pl.Series("number_of_hotels_lux", hotels_num5)
    ]).filter(pl.col('number_of_hotels') >= h3_params[2])

    return dataset


def related_distance_filter(ds_to_filter, reference_ds, h3_params):
    central_cells_h3_indexes = reference_ds[f'h3_index_{h3_params[0]}'].to_list()
    widen_cells_h3_indexes = [h3.grid_disk(cell, h3_params[1]) for cell in central_cells_h3_indexes]
    try:
        valid_cells = list(set(np.array(widen_cells_h3_indexes).flatten()))
    except:
        valid_cells = list(set(list(chain.from_iterable(widen_cells_h3_indexes))))

    ds_to_filter = ds_to_filter.filter(pl.col(f'h3_index_{h3_params[0]}').is_in(valid_cells))
    return ds_to_filter


#  Filter populated places to only valid (validity of cities is based on fun filtered_cities_h3() inner logic)
def make_filtered_data(countries_metadata, h3_data_dir, output_dir, min_pop, foc_min_pop, max_population):
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    list_of_valid_country_codes = countries_metadata['country_code'].to_list()

    for index, country in enumerate(list_of_valid_country_codes):
        raw_cities = pl.read_parquet(f'{h3_data_dir}/{country}/cities_h3.parquet').filter(
            pl.col('population') < max_population)
        airports_df = pl.read_parquet(f'{h3_data_dir}/{country}/airports_h3.parquet')
        features_df = pl.read_parquet(f'{h3_data_dir}/{country}/features_h3.parquet')
        hotels_df = pl.read_parquet(f'{h3_data_dir}/{country}/hotels_h3.parquet')
        resolution = countries_metadata.filter(pl.col('country_code') == country)['resolution'].item()
        foc_radius = countries_metadata.filter(pl.col('country_code') == country)['foc_radius'].item()
        soc_radius = countries_metadata.filter(pl.col('country_code') == country)['soc_radius'].item()
        refined_cities = filtered_cities_h3(cities_df=raw_cities, h3_resolution=resolution, foc_radius=foc_radius,
                                            soc_radius=soc_radius, min_pop=min_pop, foc_min_pop=foc_min_pop)
        os.mkdir(f'{output_dir}/{country}')
        refined_cities.write_parquet(f'{output_dir}/{country}/cities_filtered.parquet')
        airports_df.write_parquet(f'{output_dir}/{country}/airports_filtered.parquet')
        features_df.write_parquet(f'{output_dir}/{country}/features_filtered.parquet')
        hotels_df.write_parquet(f'{output_dir}/{country}/hotels_filtered.parquet')


def make_tag_data(
        h3_feature_hotel_distance,
        min_hotels_features,
        h3_city_hotel_distance,
        min_hotels_cities,
        h3_feature_city_distance,
        h3_city_airport_distance,
        relevant_feature_list,
        countries_filtered_path,
        activity_tag_dir,
        activity_tag_root_dir,
        countries_metadata_path,
):
    shutil.rmtree(f'{activity_tag_root_dir}')
    os.mkdir(activity_tag_root_dir)
    os.mkdir(f'{activity_tag_root_dir}/{activity_tag_dir}')
    list_of_valid_country_codes = countries_metadata_path['country_code'].to_list()

    for index, country in enumerate(list_of_valid_country_codes):
        os.mkdir(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}')

        airports = pl.read_parquet(f'{countries_filtered_path}/{country}/airports_filtered.parquet')
        cities = pl.read_parquet(f'{countries_filtered_path}/{country}/cities_filtered.parquet')
        features = pl.read_parquet(f'{countries_filtered_path}/{country}/features_filtered.parquet').filter(
            pl.col('feature_code').is_in(relevant_feature_list))
        hotels = pl.read_parquet(f'{countries_filtered_path}/{country}/hotels_filtered.parquet')

        # features and cities filtered by number of proxmal hotels
        features = filter_by_hotels(dataset=features, hotels=hotels,
                                    h3_params=(h3_feature_hotel_distance[0], h3_feature_hotel_distance[1],
                                               min_hotels_features))
        cities = filter_by_hotels(dataset=cities, hotels=hotels,
                                  h3_params=(h3_city_hotel_distance[0], h3_city_hotel_distance[1], min_hotels_cities))

        features = related_distance_filter(ds_to_filter=features, reference_ds=cities,
                                           h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))
        cities = related_distance_filter(ds_to_filter=cities, reference_ds=features,
                                         h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))
        airports = related_distance_filter(ds_to_filter=airports, reference_ds=cities,
                                           h3_params=(h3_city_airport_distance[0], h3_city_airport_distance[1]))
        cities = related_distance_filter(ds_to_filter=cities, reference_ds=airports,
                                         h3_params=(h3_city_airport_distance[0], h3_city_airport_distance[1]))
        features = related_distance_filter(ds_to_filter=features, reference_ds=cities,
                                           h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))

        # features

        features_filtered = features.select(
            ['geonameid', 'name', 'alternatenames', 'latitude', 'longitude', 'feature_code', 'country_code',
             'number_of_hotels',
             'number_of_hotels_lux',
             'elevation', 'h3_index_0', 'h3_index_1', 'h3_index_2', 'h3_index_3', 'h3_index_4', 'h3_index_5',
             'h3_index_6',
             'h3_index_7']).unique('geonameid')
        features_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/features.parquet')

        # cities

        cities_filtered = cities.select(
            ['geonameid', 'name', 'alternatenames', 'latitude', 'longitude', 'feature_code', 'country_code',
             'population',
             'elevation', 'number_of_hotels', 'number_of_hotels_lux', 'h3_index_0', 'h3_index_1', 'h3_index_2',
             'h3_index_3',
             'h3_index_4', 'h3_index_5', 'h3_index_6', 'h3_index_7']
        ).unique('geonameid')
        cities_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/cities.parquet')

        # airports
        airports_filtered = airports.select(
            ['geonameid', 'iata_code', 'name', 'latitude', 'longitude', 'country_code', 'type', 'h3_index_0',
             'h3_index_1',
             'h3_index_2', 'h3_index_3', 'h3_index_4', 'h3_index_5', 'h3_index_6', 'h3_index_7']).unique('geonameid')
        airports_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/airports.parquet')


def make_autocomplete_populated_places_list(
        h3_feature_hotel_distance,
        min_hotels_features,
        h3_city_hotel_distance,
        min_hotels_cities,
        h3_feature_city_distance,
        h3_city_airport_distance,
        # relevant_feature_list,
        countries_filtered_path,
        activity_tag_dir,
        activity_tag_root_dir,
        countries_metadata_path,
):
    shutil.rmtree(f'{activity_tag_root_dir}')
    os.mkdir(activity_tag_root_dir)
    os.mkdir(f'{activity_tag_root_dir}/{activity_tag_dir}')
    list_of_valid_country_codes = countries_metadata_path['country_code'].to_list()

    for index, country in enumerate(list_of_valid_country_codes):
        os.mkdir(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}')

        airports = pl.read_parquet(f'{countries_filtered_path}/{country}/airports_filtered.parquet')
        cities = pl.read_parquet(f'{countries_filtered_path}/{country}/cities_filtered.parquet')
        features = pl.read_parquet(
            f'{countries_filtered_path}/{country}/features_filtered.parquet')  # .filter(pl.col('feature_code').is_in(relevant_feature_list))
        hotels = pl.read_parquet(f'{countries_filtered_path}/{country}/hotels_filtered.parquet')

        # features and cities filtered by number of proxmal hotels
        features = filter_by_hotels(dataset=features, hotels=hotels, h3_params=(
            h3_feature_hotel_distance[0], h3_feature_hotel_distance[1], min_hotels_features))
        cities = filter_by_hotels(dataset=cities, hotels=hotels,
                                  h3_params=(h3_city_hotel_distance[0], h3_city_hotel_distance[1], min_hotels_cities))

        features = related_distance_filter(ds_to_filter=features, reference_ds=cities,
                                           h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))
        cities = related_distance_filter(ds_to_filter=cities, reference_ds=features,
                                         h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))
        airports = related_distance_filter(ds_to_filter=airports, reference_ds=cities,
                                           h3_params=(h3_city_airport_distance[0], h3_city_airport_distance[1]))
        cities = related_distance_filter(ds_to_filter=cities, reference_ds=airports,
                                         h3_params=(h3_city_airport_distance[0], h3_city_airport_distance[1]))
        features = related_distance_filter(ds_to_filter=features, reference_ds=cities,
                                           h3_params=(h3_feature_city_distance[0], h3_feature_city_distance[1]))

        # features

        features_filtered = features.select(
            ['geonameid', 'name', 'alternatenames', 'latitude', 'longitude', 'feature_code', 'country_code',
             'number_of_hotels',
             'number_of_hotels_lux',
             'elevation', 'h3_index_0', 'h3_index_1', 'h3_index_2', 'h3_index_3', 'h3_index_4', 'h3_index_5',
             'h3_index_6',
             'h3_index_7']).unique('geonameid')
        features_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/features.parquet')

        # cities

        cities_filtered = cities.select(
            ['geonameid', 'name', 'alternatenames', 'latitude', 'longitude', 'feature_code', 'country_code',
             'population',
             'elevation', 'number_of_hotels', 'number_of_hotels_lux', 'h3_index_0', 'h3_index_1', 'h3_index_2',
             'h3_index_3',
             'h3_index_4', 'h3_index_5', 'h3_index_6', 'h3_index_7']
        ).unique('geonameid')
        cities_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/cities.parquet')

        # airports
        airports_filtered = airports.select(
            ['geonameid', 'iata_code', 'name', 'latitude', 'longitude', 'country_code', 'type', 'h3_index_0',
             'h3_index_1',
             'h3_index_2', 'h3_index_3', 'h3_index_4', 'h3_index_5', 'h3_index_6', 'h3_index_7']).unique('geonameid')
        airports_filtered.write_parquet(f'{activity_tag_root_dir}/{activity_tag_dir}/{country}/airports.parquet')


def destination_raw_score(cities, metadata):
    for code in metadata['relevant_feature_list']:
        max_distance = cities[f'average_distance_to_{code}'].max()
        cities = cities.with_columns(
            pl.when(cities[
                        f'{code}_no_h{metadata["h3_feature_city_distance"][0]}_{metadata["h3_feature_city_distance"][1]}'] == 0).then(
                max_distance).otherwise(cities[f'average_distance_to_{code}']).alias(f'average_distance_to_{code}'))

        cities = cities.fill_null(1)
        max = cities[f'average_distance_to_{code}'].max()
        cities = cities.with_columns((max - cities[f'average_distance_to_{code}']).alias(f'average_distance_to_{code}'))

        cities = cities.rename({
            f'{code}_no_h{metadata["h3_feature_city_distance"][0]}_{metadata["h3_feature_city_distance"][1]}': f'no_{code}_score'})
        cities = cities.rename({f'average_distance_to_{code}': f'distance_{code}_score'})

    cities = cities.with_columns(
        (pl.col('number_of_hotels_lux') / pl.col('number_of_hotels')).alias('lux_hotel_ratio')
    )
    columns = cities.columns

    # Identify the last column
    last_col = columns[-1]

    # Move last column to index 3 (4th position)
    new_order = columns[:3] + [last_col] + columns[3:-1]

    # Reorder DataFrame
    cities = cities.select(new_order)

    columns_to_score_number = 2 * len(metadata['relevant_feature_list'])
    cities_scoring = cities.select(
        ['geonameid', 'number_of_hotels', 'number_of_hotels_lux', 'lux_hotel_ratio'] + cities.columns[
                                                                                       -columns_to_score_number:])

    weights = {col: (1, 'normal') for col in cities_scoring.columns[1:]}

    # def normalization(df, weights):
    #  for weight in weights:
    #   if weights[weight][1] == 'linear':
    #    df = df.with_columns(
    #     ((pl.col(weight) - pl.col(weight).min()) / (pl.col(weight).max() - pl.col(weight).min())).alias(weight))
    #   else:
    #    pass
    #
    #  return df
    #
    # cities_scoring = normalization(cities_scoring, weights)
    #
    # cities_scoring = cities_scoring.with_columns([
    #  cities_scoring[col] * weights[col][0] for col in cities_scoring.columns if col in weights
    # ]).fill_nan(0)
    #
    return cities_scoring, weights


def make_activity_tag(tag_name, countries_metadata, h3_data_dir, relevant_feature_list, h3_city_airport_distance,
                      h3_city_hotel_distance, h3_feature_hotel_distance, h3_feature_city_distance, min_hotels_cities,
                      min_hotels_features, foc_min_pop, max_pop=35000000, min_pop=0, output_dir='countries_filtered',
                      activity_tag_root_dir='activity_tags_raw_data', fca_folder='parquet'):
    metadata = valid_cities_mapping(countries_metadata=countries_metadata, h3_data_dir=h3_data_dir)
    make_filtered_data(
        countries_metadata=metadata,
        h3_data_dir=h3_data_dir,
        output_dir=output_dir,
        min_pop=min_pop,
        foc_min_pop=foc_min_pop,
        max_population=max_pop)
    make_tag_data(
        relevant_feature_list=relevant_feature_list,
        countries_filtered_path=output_dir,
        activity_tag_dir=tag_name,
        countries_metadata_path=countries_metadata,
        h3_city_airport_distance=h3_city_airport_distance,
        h3_city_hotel_distance=h3_city_hotel_distance,
        h3_feature_city_distance=h3_feature_city_distance,
        min_hotels_cities=min_hotels_cities,
        min_hotels_features=min_hotels_features,
        activity_tag_root_dir=activity_tag_root_dir,
        h3_feature_hotel_distance=h3_feature_hotel_distance,

    )
    raw_pandas = make_xarray(activity_tag=tag_name, countries_list=metadata['country_code'].to_list(),
                             activity_tags_root_dir=activity_tag_root_dir)
    ################### PROBA ZA 3D PARAMETRIZACIJU   #################################

    cities = raw_pandas[2]
    features = raw_pandas[1]
    airports = raw_pandas[0]
    h3_index = h3_feature_city_distance[0]
    h3_radius = h3_feature_city_distance[1]
    relevant_features = relevant_feature_list
    for code in relevant_features:
        num_of_features = []
        average_distance_per_class = []
        for index, row in cities.iterrows():
            # features = features[features['elevation'] > 2000]
            list_of_indexes = h3.grid_disk(row[f'h3_index_{h3_index}'], h3_radius)
            feature_class = features[features['feature_code'] == code]
            valid_features = feature_class[feature_class[f'h3_index_{h3_index}'].isin(list_of_indexes)]
            num_of_features.append(valid_features.shape[0])
            average_coordinate_of_features_class = (valid_features['latitude'].mean(),
                                                    valid_features['longitude'].mean())
            average_distance_to_feature_class = haversine(row['latitude'], row['longitude'],
                                                          average_coordinate_of_features_class[0],
                                                          average_coordinate_of_features_class[1])
            average_distance_per_class.append(average_distance_to_feature_class)

        cities[f'{code}_no_h{h3_index}_{h3_radius}'] = num_of_features
        cities[f'average_distance_to_{code}'] = average_distance_per_class
    if os.path.exists(f'{fca_folder}/{tag_name}'):
        shutil.rmtree(f'{fca_folder}/{tag_name}')
        mkdir(f'{fca_folder}/{tag_name}')
        airports.to_parquet(f'{fca_folder}/{tag_name}/airports.parquet')
        cities.to_parquet(f'{fca_folder}/{tag_name}/cities.parquet')
        features.to_parquet(f'{fca_folder}/{tag_name}/features.parquet')
    else:
        mkdir(f'{fca_folder}/{tag_name}')
        airports.to_parquet(f'{fca_folder}/{tag_name}/airports.parquet')
        cities.to_parquet(f'{fca_folder}/{tag_name}/cities.parquet')
        features.to_parquet(f'{fca_folder}/{tag_name}/features.parquet')

    metadata = {"tag_name": tag_name,
                "relevant_feature_list": relevant_feature_list,
                "h3_city_airport_distance": h3_city_airport_distance,
                "h3_city_hotel_distance": h3_city_hotel_distance,
                "h3_feature_hotel_distance": h3_feature_hotel_distance,
                "h3_feature_city_distance": h3_feature_city_distance,
                "min_hotels_cities": min_hotels_cities,
                "min_hotels_features": min_hotels_features,
                "foc_min_pop": foc_min_pop,
                "max_pop": max_pop,
                "min_pop": min_pop
                }

    with open(f"{fca_folder}/{tag_name}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    cities_scoring = destination_raw_score(cities=pl.from_pandas(cities), metadata=metadata)

    with open(f"{fca_folder}/{tag_name}/weights.json", "w") as f:
        json.dump(cities_scoring[1], f, indent=4)
    cities_scoring[0].write_parquet(f'{fca_folder}/{tag_name}/score_matrix.parquet')

    ###################################################################################


def make_autocomplete(tag_name, countries_metadata, h3_data_dir, h3_city_airport_distance,
                      h3_city_hotel_distance, h3_feature_hotel_distance, h3_feature_city_distance, min_hotels_cities,
                      min_hotels_features, foc_min_pop, max_pop, min_pop, output_dir='countries_filtered',
                      activity_tag_root_dir='activity_tags_raw_data'):
    metadata = valid_cities_mapping(countries_metadata=countries_metadata, h3_data_dir=h3_data_dir)
    make_filtered_data(
        countries_metadata=metadata,
        h3_data_dir=h3_data_dir,
        output_dir=output_dir,
        min_pop=min_pop,
        foc_min_pop=foc_min_pop,
        max_population=max_pop)
    make_autocomplete_populated_places_list(
        countries_filtered_path=output_dir,
        activity_tag_dir=tag_name,
        countries_metadata_path=countries_metadata,
        h3_city_airport_distance=h3_city_airport_distance,
        h3_city_hotel_distance=h3_city_hotel_distance,
        h3_feature_city_distance=h3_feature_city_distance,
        min_hotels_cities=min_hotels_cities,
        min_hotels_features=min_hotels_features,
        activity_tag_root_dir=activity_tag_root_dir,
        h3_feature_hotel_distance=h3_feature_hotel_distance,

    )
    make_xarray(activity_tag=tag_name, countries_list=metadata['country_code'].to_list(),
                activity_tags_root_dir=activity_tag_root_dir)


def make_xarray(activity_tag, countries_list, activity_tags_root_dir, activity_arrays='activity_arrays'):
    xarray_ds = []

    ##########PROBA##########
    airports_integral = []
    features_integral = []
    cities_integral = []

    ##########################
    for country in countries_list:

        try:
            airports_tag = pl.read_parquet(
                f'{activity_tags_root_dir}/{activity_tag}/{country}/airports.parquet').to_pandas()
            airports_integral.append(airports_tag)  # PROBA
            cities_tag = pl.read_parquet(
                f'{activity_tags_root_dir}/{activity_tag}/{country}/cities.parquet').to_pandas()
            cities_integral.append(cities_tag)  # PROBA
            features_tag = pl.read_parquet(
                f'{activity_tags_root_dir}/{activity_tag}/{country}/features.parquet').to_pandas()
            features_integral.append(features_tag)  # PROBA

            xarray_ds.append(make_xarray_ds(airports_df=airports_tag, cities_df=cities_tag, features_df=features_tag))
        except:
            print(country)
    all = xr.merge(xarray_ds)
    if os.path.exists(f'{activity_arrays}/{activity_tag}.zarr'):
        shutil.rmtree(f'{activity_arrays}/{activity_tag}.zarr')
        all.to_zarr(f'{activity_arrays}/{activity_tag}.zarr')
    else:
        all.to_zarr(f'{activity_arrays}/{activity_tag}.zarr')

    # PROBA
    airports_pandas = pd.concat(airports_integral, ignore_index=True)
    features_pandas = pd.concat(features_integral, ignore_index=True)
    cities_pandas = pd.concat(cities_integral, ignore_index=True)

    # DIO PROBE ZA 3D #########################

    # if os.path.exists(f'parquet/{activity_tag}'):
    #     shutil.rmtree(f'parquet/{activity_tag}')
    #     mkdir(f'parquet/{activity_tag}')
    #     airports_parquet.to_parquet(f'parquet/{activity_tag}/airports.parquet')
    #     cities_parquet.to_parquet(f'parquet/{activity_tag}/cities.parquet')
    #     features_parquet.to_parquet(f'parquet/{activity_tag}/features.parquet')
    # else:
    #     mkdir(f'parquet/{activity_tag}')
    #     airports_parquet.to_parquet(f'parquet/{activity_tag}/airports.parquet')
    #     cities_parquet.to_parquet(f'parquet/{activity_tag}/cities.parquet')
    #     features_parquet.to_parquet(f'parquet/{activity_tag}/features.parquet')

    #############################################################
    return airports_pandas, features_pandas, cities_pandas


# Merge all relevant data into xarray dataset
def make_xarray_ds(airports_df, cities_df, features_df):
    # Create a unified list of all unique geonameid values across all DataFrames
    all_geonameids = np.unique(np.concatenate([airports_df['geonameid'].to_numpy(),
                                               cities_df['geonameid'].to_numpy(),
                                               features_df['geonameid'].to_numpy()]))

    # Create coordinate arrays for the xarray dimensions
    airport_coords = np.array(airports_df['geonameid'])
    cities_coords = np.array(cities_df['geonameid'])
    features_coords = np.array(features_df['geonameid'])

    # Initialize variables dictionary
    variables = {}

    # Add airport data, using 'geonameid' for the index
    for col in airports_df.columns:
        if col in ['iata_code', 'name', 'latitude', 'longitude', 'country_code', 'type',
                   'h3_index_0, h3_index1']:  # Skip and 'geonameid'
            variables[f'airports_{col}'] = (['airports'], airports_df[col].to_numpy())

    # Add city data, using 'geonameid' for the index
    for col in cities_df.columns:
        if col in ['name', 'latitude', 'longitude', 'feature_code', 'country_code', 'population',
                   'elevation', 'number_of_hotels', 'number_of_hotels_lux',
                   'h3_index_0, h3_index1']:  # Skip 'geonameid'
            variables[f'cities_{col}'] = (['cities'], cities_df[col].to_numpy())

    # Add feature data, using 'geonameid' for the index
    for col in features_df.columns:
        if col in col in ['name', 'latitude', 'longitude', 'feature_code', 'country_code',
                          'elevation', 'number_of_hotels', 'number_of_hotels_lux',
                          'h3_index_0, h3_index1']:  # Skip 'geonameid'
            variables[f'features_{col}'] = (['features'], features_df[col].to_numpy())

    # Create the xarray dataset
    dataset = xr.Dataset(variables, coords={
        'geonameid': all_geonameids,  # Unified geonameid coordinate
        'airports': airport_coords,
        'cities': cities_coords,
        'features': features_coords
    })

    return dataset


def apply_masks(dataset, cf_distance, ac_distance):
    # Adjust Dask arrays if already loaded as Dask arrays
    cities_latitude_da = dataset['cities_latitude'].data.rechunk((500,))
    cities_longitude_da = dataset['cities_longitude'].data.rechunk((500,))
    features_latitude_da = dataset['features_latitude'].data.rechunk((500,))
    features_longitude_da = dataset['features_longitude'].data.rechunk((500,))

    # Broadcasting for distance calculation
    cities_latitude_broadcasted = cities_latitude_da[:, None]  # Shape: [cities, 1]
    cities_longitude_broadcasted = cities_longitude_da[:, None]  # Shape: [cities, 1]

    # Calculate distances with broadcasting
    city_feature_distances = haversine(
        cities_latitude_broadcasted,
        cities_longitude_broadcasted,
        features_latitude_da,
        features_longitude_da
    )

    # Create the boolean mask
    feature_near_city_mask = city_feature_distances < cf_distance

    # Track progress during computation
    with ProgressBar():
        computed_mask = feature_near_city_mask.compute()

    # Convert computed mask into an Xarray DataArray
    standard_xarray_mask = xr.DataArray(
        computed_mask,
        dims=['cities', 'features'],
        coords={'cities': dataset['cities'], 'features': dataset['features']},
        name='feature_near_city_mask'
    )

    # Add the mask to the dataset
    dataset['feature_near_city'] = (['cities', 'features'], standard_xarray_mask.data)

    # Step 1: Adjust Dask arrays by rechunking if needed (already Dask arrays from .zarr)
    airports_latitude_da = dataset['airports_latitude'].data.rechunk((dataset.sizes['airports'],))
    airports_longitude_da = dataset['airports_longitude'].data.rechunk((dataset.sizes['airports'],))
    cities_latitude_da = dataset['cities_latitude'].data.rechunk((dataset.sizes['cities'],))
    cities_longitude_da = dataset['cities_longitude'].data.rechunk((dataset.sizes['cities'],))

    # Step 2: Broadcast cities' latitudes and longitudes to match airport dimensions for vectorized calculation
    cities_latitude_broadcasted = cities_latitude_da[None, :]  # Shape: [1, cities], broadcasts to [airports, cities]
    cities_longitude_broadcasted = cities_longitude_da[None, :]  # Shape: [1, cities]

    # Step 3: Broadcast airports' latitudes and longitudes to match city dimensions
    airports_latitude_broadcasted = airports_latitude_da[:,
                                    None]  # Shape: [airports, 1], broadcasts to [airports, cities]
    airports_longitude_broadcasted = airports_longitude_da[:, None]  # Shape: [airports, 1]

    # Step 4: Calculate the distance matrix using haversine (vectorized)
    city_airport_distances = haversine(
        cities_latitude_broadcasted,
        cities_longitude_broadcasted,
        airports_latitude_broadcasted,
        airports_longitude_broadcasted
    )

    # Step 5: Create the mask: True if the distance is less than 150 km, False otherwise
    city_near_airport_mask = city_airport_distances < ac_distance

    # Track progress using Dask's ProgressBar
    with ProgressBar():
        # Step 6: Compute the Dask array to get a standard NumPy array
        computed_mask = city_near_airport_mask.compute()

    # Step 7: Convert the computed mask into a standard Xarray DataArray
    standard_xarray_mask = xr.DataArray(
        computed_mask,  # The computed boolean mask data
        dims=['airports', 'cities'],  # Dimensions for the mask
        coords={'airports': dataset['airports'], 'cities': dataset['cities']},  # Use original coordinates
        name='city_near_airport_mask'  # Optional name for the DataArray
    )

    # Step 8: Add the mask to the dataset
    dataset['city_near_airport'] = (['airports', 'cities'], standard_xarray_mask.data)

    variables = [
        'airports_country_code',
        'airports_iata_code',
        'airports_name',
        'airports_type',
        'cities_country_code',
        'cities_feature_code',
        'cities_name',
        'features_country_code',
        'features_feature_code',
        'features_name'
    ]

    for variable in variables:
        dataset[variable] = dataset[variable].astype('<U20')
        dataset[variable] = dataset[variable].where(dataset[variable].notnull(), 'missing_value')

    return dataset


def find_proximal_cities_to_airport(dataset, airport_iata_code):
    # Locate the index of the airport in the dataset based on 'iata_code'
    airport_index = np.where(dataset['airports_iata_code'].values == airport_iata_code)[0][0]

    # Compute the boolean mask to ensure compatibility with Xarray's indexing
    boolean_mask = dataset['city_near_airport'].isel(airports=airport_index).compute()

    # Use the computed boolean mask for indexing
    proximal_cities_to_specific_airport = dataset['cities'].where(boolean_mask, drop=True)

    return proximal_cities_to_specific_airport


def find_proximal_features_to_city(dataset, city_name):
    # Find the index of the city
    city_index = np.where(dataset['cities_name'].values == city_name)[0][0]

    # Compute the boolean mask to ensure it is a NumPy array
    boolean_mask = dataset['feature_near_city'].isel(cities=city_index).compute()

    # Use the computed boolean mask for indexing
    proximal_features_to_specific_city = dataset['features'].where(boolean_mask, drop=True)
    return proximal_features_to_specific_city


def normalization_score(df, weights):
    for weight in weights:
        if weights[weight][1] == 'normal':
            df = df.with_columns(
                ((pl.col(weight) - pl.col(weight).min()) / (pl.col(weight).max() - pl.col(weight).min())).alias(weight))
        else:
            pass
    return df


def get_scored_cities(weights, metadata, airports, cities, score_matrix):
    cities_scoring = normalization_score(score_matrix, weights)

    df = cities_scoring.with_columns([
        cities_scoring[col] * weights[col][0] for col in cities_scoring.columns if col in weights
    ]).fill_nan(0)

    df = df.with_columns(
        pl.sum_horizontal(pl.all().exclude("geonameid")).alias("static_score"))
    result = cities.join(df.select(["geonameid", "static_score"]), on="geonameid", how="left").sort(by="static_score",
                                                                                                    descending=True)
    airport_index = result.select(pl.col(f'h3_index_{metadata["h3_city_airport_distance"][0]}')).to_series().to_list()
    allowed_airport_indexes = [h3.grid_disk(index, metadata["h3_city_airport_distance"][1]) for index in airport_index]
    nearby_airports = [
        airports.filter(pl.col(f'h3_index_{metadata["h3_city_airport_distance"][0]}').is_in(allowed_index))[
            'iata_code'].to_list() for allowed_index in allowed_airport_indexes]
    final_result = result.with_columns(
        pl.Series("airports", nearby_airports)  # Create a new column named "B"
    )

    return final_result


def nearest_city(coordinates, autocomplete_cities=autocomplete_cities):
    allowed_indexes = [(6, 0), (6, 1), (5, 0), (5, 1), (4, 0), (4, 1), (3, 0), (3, 1)]
    for h3_index_radius in allowed_indexes:
        autocomplete_city_index = h3.latlng_to_cell(coordinates[0], coordinates[1], h3_index_radius[0])
        grid_disk = h3.grid_disk(autocomplete_city_index, h3_index_radius[1])
        found_cities = autocomplete_cities.filter(pl.col(f'h3_index_{h3_index_radius[0]}').is_in(grid_disk))
        if found_cities.height != 0:
            break

        else:
            pass

    found_list = list(zip(found_cities["lat"], found_cities["lng"]))
    distances = hs.haversine_vector(coordinates, found_list, comb=True).flatten().tolist()
    found_cities = found_cities.with_columns(pl.Series("distance", distances)).sort(by="distance",
                                                                                    descending=False).head(
        1)  # .to_dicts()[0]

    return found_cities


def search_area(trip_duration):
    if trip_duration == 0:
        car_radius = (5, 1)
        flight_radius = None
        starting_airport_radius = (5, 1)
    elif trip_duration == 1:
        car_radius = (4, 1)
        flight_radius = (1, 1)
        starting_airport_radius = (5, 1)
    elif trip_duration == 2:
        car_radius = (3, 1)
        flight_radius = (1, 1)
        starting_airport_radius = (4, 1)
    elif trip_duration == 3:
        car_radius = (3, 1)
        flight_radius = (1, 1)
        starting_airport_radius = (4, 1)
    elif trip_duration == 4:
        car_radius = (3, 1)
        flight_radius = (1, 1)
        starting_airport_radius = (4, 1)
    elif trip_duration == 5:
        car_radius = (3, 1)
        flight_radius = (0, 1)
        starting_airport_radius = (4, 1)
    elif 5 < trip_duration < 7:
        car_radius = (3, 1)
        flight_radius = (0, 1)
        starting_airport_radius = (3, 1)
    elif 7 <= trip_duration <= 10:
        car_radius = (1, 1)
        flight_radius = (0, 2)
        starting_airport_radius = (3, 1)
    else:
        car_radius = (0, 1)
        flight_radius = 'all'
        direct_flight_radius = 'all'
        starting_airport_radius = (2, 1)
    return {'car_radius': car_radius, 'flight': flight_radius, 'starting_airport': starting_airport_radius}


def add_h3_index_polars(df, lat_col, lon_col):
    all_indexes = []
    for j in range(8):
        h3_index = []
        for row in df.to_dicts():
            h3_index.append(h3.latlng_to_cell(row[lat_col], row[lon_col], j))
        all_indexes.append(h3_index)
    for i in range(8):
        df = df.with_columns([
            pl.Series(f"h3_index_{i}", all_indexes[i]),
        ])
    return df


def get_result(search_params, autocomplete_cities=autocomplete_cities):
    logger.info("get_res")

    try:
        start_date = datetime.strptime(search_params["start_date_string"], "%Y-%m-%d")
    except:
        start_date = ""
    try:
        end_date = datetime.strptime(search_params["end_date_string"], "%Y-%m-%d")
    except:
        end_date = start_date

    trip_duration = (end_date - start_date).days
    start_point = autocomplete_cities.filter(pl.col("id") == int(search_params["id"]))

    search_area_params = search_area(trip_duration)

    logger.info("importing relevant data")

    search_params_prepared = "peaks"
    if search_params["activity_tag"] in [
        "skiing",
        "hiking",
        "family_trip",
        "lakes",
        "parachuting",
    ]:
        search_params_prepared = "summer"

    if search_params["activity_tag"] in ["caving, mountains"]:
        search_params_prepared = "peaks"

    if search_params["activity_tag"] in ["summer_vacation"]:
        search_params_prepared = "summer"

    # importing relevant data
    file_path_cities_parquet = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/cities.parquet",
    )
    file_path_airports_parquet = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/airports.parquet",
    )
    file_path_metadata_json = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/metadata.json",
    )
    file_path_score_matrix_parquet = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/score_matrix.parquet",
    )
    file_path_weights_json = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/weights.json",
    )
    file_path_features_parquet = os.path.join(
        settings.BASE_DIR,
        "backend/",
        f"parquet/{search_params_prepared}/features.parquet",
    )

    logger.info("read parquets")
    cities = pl.read_parquet(file_path_cities_parquet)
    airports = pl.read_parquet(file_path_airports_parquet)

    score_matrix = pl.read_parquet(file_path_score_matrix_parquet)
    weights = json.load(open(file_path_weights_json))
    metadata = json.load(open(file_path_metadata_json))
    features = pl.read_parquet(file_path_features_parquet)
    feature_city_distance = metadata["h3_feature_city_distance"]
    relevant_feature_list = metadata['relevant_feature_list']

    car_radius = search_area_params['car_radius']
    flight_radius = search_area_params['flight']
    # direct_flight_trip = search_area_params['direct_flight']

    # nearby airports codes
    top_airports = search_params["airports"]
    logger.info("top airports")
    logger.info(top_airports)
    # allowed cities
    scored_cities = get_scored_cities(cities=cities, score_matrix=score_matrix, weights=weights, airports=airports,
                                      metadata=metadata)
    columns_to_fetch = ['geonameid', 'name', 'country_code', 'latitude', 'longitude', 'transport', 'departures',
                        'arrivals', 'static_score'] + [
                           f'{feature}_no_h{feature_city_distance[0]}_{feature_city_distance[1]}' for feature in
                           relevant_feature_list] + [f'average_distance_to_{feature}' for feature in
                                                     relevant_feature_list]
    logger.info("columns to fetch")
    logger.info(columns_to_fetch)

    if trip_duration == 0:
        car_trip_df = features
    else:
        car_trip_df = scored_cities

    car_trip_results = car_trip_df.filter(pl.col(f'h3_index_{car_radius[0]}').is_in(
        h3.grid_disk(start_point[f"h3_index_{car_radius[0]}"][0], car_radius[1])))
    n = 1
    while car_trip_results.height == 0:
        car_trip_results = car_trip_df.filter(pl.col(f'h3_index_{car_radius[0] - n}').is_in(
            h3.grid_disk(start_point[f"h3_index_{car_radius[0] - n}"][0], car_radius[1])))
        n += 1
    car_trip_results = car_trip_results.with_columns([
        pl.lit('car').alias("transport"), pl.lit([]).alias("departures"), pl.lit([]).alias("arrivals")]).head(
        min(car_trip_results.height, 60))

    logger.info("flight results")
    if flight_radius != None:
        if flight_radius == 'all':
            flight_trip_results = scored_cities
        else:
            flight_trip_results = scored_cities.filter(pl.col(f'h3_index_{flight_radius[0]}').is_in(
                h3.grid_disk(start_point[f'h3_index_{flight_radius[0]}'][0], flight_radius[1])))
            n = 1
            while flight_trip_results.height == 0:
                flight_trip_results = scored_cities.filter(pl.col(f'h3_index_{flight_radius[0] - n}').is_in(
                    h3.grid_disk(start_point[f"h3_index_{flight_radius[0] - n}"][0], flight_radius[1])))
                n += 1
        flight_trip_results = flight_trip_results.with_columns([
            pl.lit('non_direct').alias("transport"), pl.lit([]).alias("departures"), pl.lit([]).alias("arrivals")])
        try:
            direct_flights_raw = reachable_airports(search_params=search_params, top_airports=top_airports)
            # print(direct_flights_raw)
            flight_results = add_direct_flights(raw_ae=direct_flights_raw, static_flights=flight_trip_results)
            direct_flight_trip_results = flight_results.filter(pl.col('transport') == 'direct')
            flight_trip_results = flight_results.filter(pl.col('transport') != 'direct')
            flight_trip_results = mix_flights(direct=direct_flight_trip_results, non_direct=flight_trip_results)
        except:
            direct_flight_trip_results = 'no results'
    else:
        direct_flight_trip_results = 'no results'
        flight_trip_results = 'no results'

    if trip_duration != 0:
        # try:
        flight_struct = pl.Struct([
            pl.Field("departure", pl.String),
            pl.Field("arrival", pl.String),
            pl.Field("departureTime", pl.String),
            pl.Field("arrivalTime", pl.String),
            pl.Field("airline:", pl.String),  # be careful: "airline:" has a colon; is that intentional?
            pl.Field("airlineCode", pl.String),
        ])

        car_trip_results = car_trip_results.with_columns([
            pl.lit("car").alias("transport"),
            pl.lit([]).cast(pl.List(flight_struct)).alias("departures"),
            pl.lit([]).cast(pl.List(flight_struct)).alias("arrivals"),
        ])
        try:
            mix = top_mix(car=car_trip_results, flights=flight_trip_results)
            mix = mix.head(min(mix.height, 60))
        except:
            mix = car_trip_results.head(min(car_trip_results.height, 60))
        flight_trip_results = flight_trip_results.head(60).select(columns_to_fetch).to_dicts()
        mix = mix.select(columns_to_fetch).to_dicts()
        logger.info("car trip results")
        car_trip_results = car_trip_results.select(columns_to_fetch)

    else:
        logger.info("car trip results TYPEE")
        logger.info(type(car_trip_results))

        if (type(car_trip_results) != 'list'):
            mix = car_trip_results.head(60).select([
                'geonameid',
                'name',
                'alternatenames',
                'latitude',
                'longitude',
                'feature_code',
                'country_code',
            ]).to_dicts()
        else:
            mix = car_trip_results.head(60).select([
                'geonameid',
                'name',
                'alternatenames',
                'latitude',
                'longitude',
                'feature_code',
                'country_code',
            ])

        logger.info('final car trip results type')
        logger.info(type(car_trip_results))

        logger.info('final car trip results')
        logger.info(car_trip_results)

        if (trip_duration == 0):
            try:
                mix = car_trip_results.to_dicts()
            except:
                mix = car_trip_results

    return {'top': mix, 'car': car_trip_results.to_dicts(), 'flight': flight_trip_results}


def get_nearest_airports_with_large_constraint(
        df: pl.DataFrame,
        n_total: int = 3,
        min_large: int = 1,
        distance_col: str = "distance",
        type_col: str = "type",
        id_col: str = "iata_code"
) -> pl.DataFrame:
    # Sort all airports by distance
    df_sorted = df.sort(distance_col)

    # Step 1: Take the closest n_total
    top_nearest = df_sorted.head(n_total)

    # Step 2: Count how many large_airports are in top_nearest
    large_in_top = (top_nearest[type_col] == "large_airport").sum()

    if large_in_top >= min_large:
        return top_nearest

    # Step 3: Force in more large airports (if available)
    large_airports = df_sorted.filter(pl.col(type_col) == "large_airport").head(min_large)

    # Step 4: Fill remaining with other closest, excluding already selected
    excluded_ids = large_airports[id_col].unique()
    additional = df_sorted.filter(~pl.col(id_col).is_in(excluded_ids)).head(n_total - large_airports.height)

    # Combine and sort again
    result = pl.concat([large_airports, additional]).sort(distance_col)

    return result


def nearby_airports(search_params, airports=3, large_airports=1, autocomplete_cities=autocomplete_cities,
                    all_airports=all_airports):
    start_date = datetime.strptime(search_params["start_date_string"], "%Y-%m-%d")
    end_date = datetime.strptime(search_params["end_date_string"], "%Y-%m-%d")
    trip_duration = (end_date - start_date).days
    start_point = autocomplete_cities.filter(pl.col('id') == int(search_params["id"]))

    search_area_params = search_area(trip_duration)
    start_airports_index_radius = search_area_params['starting_airport']

    allowed_airports = all_airports.filter(
        pl.col(f'h3_index_{start_airports_index_radius[0]}').is_in(
            h3.grid_disk(
                start_point[f'h3_index_{start_airports_index_radius[0]}'][0], start_airports_index_radius[1]
            )
        )
    )

    n = 1
    while allowed_airports.height == 0:
        allowed_airports = all_airports.filter(pl.col(f'h3_index_{start_airports_index_radius[0] - n}').is_in(
            h3.grid_disk(start_point[f"h3_index_{start_airports_index_radius[0] - n}"][0],
                         start_airports_index_radius[1])))
        n += 1

    coordinates = start_point['lat'][0], start_point['lng'][0]
    found_list = list(zip(allowed_airports["latitude_deg"], allowed_airports["longitude_deg"]))
    distances = hs.haversine_vector(coordinates, found_list, comb=True).flatten().tolist()
    allowed_airports = allowed_airports.with_columns(pl.Series("distance", distances)).sort(by="distance",
                                                                                            descending=False)
    result = get_nearest_airports_with_large_constraint(df=allowed_airports, n_total=airports, min_large=large_airports)

    return result


def reachable_airports(search_params, top_airports):
    departure_date = search_params['start_date_string']
    return_date = search_params['end_date_string']

    def call_API_destinations(url):
        response = requests.get(url)
        return response.json()

    # Generate URLs for each departure location (2 per location)
    list_bodies = []
    for loc in top_airports:
        list_bodies.append(
            f'https://aviation-edge.com/v2/public/flightsFuture?iataCode={loc}&type=departure&date={departure_date}&key={ApiKeys.aviation_edge_key}'
        )
        list_bodies.append(
            f'https://aviation-edge.com/v2/public/flightsFuture?iataCode={loc}&type=arrival&date={return_date}&key={ApiKeys.aviation_edge_key}'
        )

    results = []
    with futures.ThreadPoolExecutor(max_workers=len(list_bodies)) as executor:
        for result in executor.map(call_API_destinations, list_bodies):
            results.append(result)

    # Organize results by location
    structured = {}
    for idx, loc in enumerate(top_airports):
        structured[loc] = {
            "departures": results[idx * 2],
            "arrivals": results[idx * 2 + 1]
        }
    for key in list(structured.keys()):
        departures = structured[key]["departures"]
        arrivals = structured[key]["arrivals"]

        if not isinstance(departures, list) or not isinstance(arrivals, list):
            structured.pop(key)

    return structured


def include_ae(all_flight_destinations, direct_flight_destinations):
    to_destination_airports = {}
    for key in all_flight_destinations.keys():
        iata_codes = jmespath.search(f"{key}.departures[*].arrival.iataCode", all_flight_destinations)
        to_destination_airports.update({key: iata_codes})
        to_destination_airports.update({key: list(set(to_destination_airports[key]))})

    from_destination_airports = {}
    for key in all_flight_destinations.keys():
        iata_codes = jmespath.search(f"{key}.arrivals[*].departure.iataCode", all_flight_destinations)
        from_destination_airports.update({key: iata_codes})
        from_destination_airports.update({key: list(set(from_destination_airports[key]))})

    to_destination_airports = [to_destination_airports[key] for key in to_destination_airports.keys()]
    from_destination_airports = [from_destination_airports[key] for key in from_destination_airports.keys()]
    all_from_origin = list(set(list(chain.from_iterable(to_destination_airports))))
    all_to_origin = list(set(list(chain.from_iterable(from_destination_airports))))
    conditions = [pl.col('airports').list.contains(airport.upper()) for airport in all_from_origin]
    df_new = direct_flight_destinations.with_columns(
        pl.reduce(lambda a, b: a | b, conditions).alias('from destination'),
    )
    conditions = [pl.col('airports').list.contains(airport.upper()) for airport in all_to_origin]
    df_new = df_new.with_columns(
        pl.reduce(lambda a, b: a | b, conditions).alias('to destination'))
    result = df_new.filter((pl.col('to destination') == True) & (pl.col('from destination') == True))
    return result


def any_transport(direct_flights, flight, car):
    direct_flights = direct_flights.head(50).sample((min(direct_flights.height, 30)))
    flight = flight.head(50).sample((min(flight.height, 20)))
    car = car.head(50).sample(min(car.height, 10))

    c = pl.concat([direct_flights, flight, car], how="diagonal").group_by('country_code', maintain_order=True).head(3)
    c = c.sample(min(c.height, 60), shuffle=True)
    return c


def connected_destinations(raw_ae):
    # Remove 'codeshared' flights
    raw_ae = {
        airport: {
            "departures": [f for f in info.get("departures", []) if "codeshared" not in f],
            "arrivals": [f for f in info.get("arrivals", []) if "codeshared" not in f]
        }
        for airport, info in raw_ae.items()
    }

    to_destinations = {}
    from_destinations = {}

    for airport in raw_ae:
        # Extract departures
        departures = raw_ae[airport].get("departures", [])
        arrivals = raw_ae[airport].get("arrivals", [])

        to_data = zip(
            jmespath.search(f"{airport}.departures[*].arrival.iataCode", raw_ae),
            jmespath.search(f"{airport}.departures[*].departure.scheduledTime", raw_ae),
            jmespath.search(f"{airport}.departures[*].arrival.scheduledTime", raw_ae),
            jmespath.search(f"{airport}.departures[*].airline.name", raw_ae),
            jmespath.search(f"{airport}.departures[*].airline.iataCode", raw_ae),
        )

        from_data = zip(
            jmespath.search(f"{airport}.arrivals[*].departure.iataCode", raw_ae),
            jmespath.search(f"{airport}.arrivals[*].departure.scheduledTime", raw_ae),
            jmespath.search(f"{airport}.arrivals[*].arrival.scheduledTime", raw_ae),
            jmespath.search(f"{airport}.arrivals[*].airline.name", raw_ae),
            jmespath.search(f"{airport}.arrivals[*].airline.iataCode", raw_ae),
        )

        # Deduplicate
        to_set = {
            (
                code.upper(),
                dep_time,
                arr_time,
                airline.title(),
                code2.upper()
            )
            for code, dep_time, arr_time, airline, code2 in to_data
        }

        from_set = {
            (
                code.upper(),
                dep_time,
                arr_time,
                airline.title(),
                code2.upper()
            )
            for code, dep_time, arr_time, airline, code2 in from_data
        }

        to_destinations[airport] = list(to_set)
        from_destinations[airport] = list(from_set)

    return to_destinations, from_destinations


def all_flights(flights_ds, structured_ae):
    all_arrivals = []
    all_departures = []
    for i in range(flights_ds.height):
        s = flights_ds[i]['airports'][0]

        a = structured_ae[1]
        d = structured_ae[0]

        # Build list of (key, common_element) tuples
        s_set = set(s.to_list())

        # Get (key, first_element) if first_element is in the Series
        result_departures = [
            {'departure': k, 'arrival': val[0], 'departureTime': val[1], 'arrivalTime': val[2], 'airline:': val[3],
             'airlineCode': val[4]} for k, values in d.items() for val in values if val[0] in s_set]
        result_arrivals = [
            {'departure': val[0], 'arrival': k, 'departureTime': val[1], 'arrivalTime': val[2], 'airline:': val[3],
             'airlineCode': val[4]} for k, values in a.items() for val in values if val[0] in s_set]
        all_arrivals.append(result_arrivals)
        all_departures.append(result_departures)
    flights_ds = flights_ds.with_columns([
        pl.Series("departures", all_departures),
        pl.Series("arrivals", all_arrivals)
    ])

    return flights_ds


def add_direct_flights(raw_ae, static_flights):
    structured_ae = connected_destinations(raw_ae=raw_ae)
    direct_flights = all_flights(flights_ds=static_flights, structured_ae=structured_ae).with_columns(
        pl.when(
            (pl.col("departures").list.len() > 0) &
            (pl.col("arrivals").list.len() > 0)
        )
        .then(pl.lit("direct"))
        .otherwise(pl.lit("non_direct"))
        .alias("transport")
    )

    return direct_flights


def results_mix(car, flight, direct_flight):
    polars = pl.dataframe.frame.DataFrame
    all = [car, flight, direct_flight]
    for_concat = []
    for result in all:
        if type(result) == polars:
            for_concat.append(result)
    try:
        final = pl.concat(for_concat, how="diagonal")
        final = final.sample(min(final.height, 60), shuffle=True)
    except:
        final = 'no results'

    return final


def mix_flights(direct, non_direct, direct_head=20, non_direct_head=20, direct_sample=50, non_direct_sample=50,
                total_mix=20):
    head20direct = direct.sample(direct.height, shuffle=True).head(min(direct_head, direct.height))
    head20non_direct = non_direct.head(min(non_direct_sample, non_direct.height)).sample(
        min(non_direct_sample, non_direct.height), shuffle=True).head(min(non_direct_head, non_direct.height))
    direct_rest = direct.join(head20direct, how="anti", on='geonameid')
    non_direct_rest = non_direct.join(head20non_direct, how="anti", on='geonameid')

    if head20direct.height != 0:
        top_merged = pl.concat([head20direct, head20non_direct]).head(
            min(int(head20direct.height * 1.5), direct_sample)).sample(
            min(int(head20direct.height * 1.5), direct_sample), shuffle=True)
    else:
        top_merged = head20non_direct.head(min(head20non_direct.height, non_direct_head)).sample(
            min(head20non_direct.height, non_direct_head), shuffle=True)
    rest_merged = pl.concat([direct_rest, non_direct_rest])
    final = pl.concat([top_merged, rest_merged])
    return final


def top_mix(car, flights, car_head=15, flights_head=20, car_sample=50, flights_sample=50, total_mix=20):
    head20car = car.head(min(car_sample, car.height)).sample(min(car_sample, car.height), shuffle=True).head(
        min(car_head, car.height))
    head20flights = flights.head(min(flights_sample, flights.height)).sample(min(flights_sample, flights.height),
                                                                             shuffle=True).head(
        min(flights_head, flights.height))
    car_rest = car.join(head20car, how="anti", on='geonameid')
    flights_rest = flights.join(head20flights, how="anti", on='geonameid')
    top_merged = pl.concat([head20car, head20flights], how='diagonal').sample(
        min(total_mix, head20car.height + head20flights.height), shuffle=True)
    top_merged = deduplicate_by_geonameid_prefer_car(top_merged)
    rest_merged = pl.concat([car_rest, flights_rest], how='diagonal').sample(car_rest.height + flights_rest.height,
                                                                             shuffle=True)
    result = pl.concat([top_merged, rest_merged])
    return result


def deduplicate_by_geonameid_prefer_car(df: pl.DataFrame) -> pl.DataFrame:
    result = (
        df
        .with_row_index(name="row_idx")  # Preserve original order
        .with_columns(
            pl.when(pl.col("transport") == "car")
            .then(1)
            .otherwise(2)
            .alias("priority")
        )
        .sort(["geonameid", "priority"])  # Sort so 'car' comes first
        .unique(subset="geonameid", keep="first")  # Keep best per geonameid
        .sort("row_idx")  # Restore original order
        .drop(["row_idx", "priority"])  # Clean up helper columns
    )
    return result


import json
from typing import List, Dict, Union
from openai import OpenAI


def get_activity_recommendations(
        start_date: str,
        end_date: str,
        activity: str,
        destination_city: str,
        destination_state: str,
        transport_type: str
) -> Dict[str, Union[List[str], Dict[str, str], str]]:
    """
    Generate activity-based travel recommendations for a city and date range.

    Returns a dict with strict structure:
    {
        "what_attraction_to_visit_regarding_activity": [str, str, ...],
        "what_is_best_to_do_on_chosen_dates": {
            "YYYY-MM-DD": "description",
            ...
        }
    }

    If structure is invalid or response cannot be parsed, returns:
    {
        "error": "error message",
        "raw_output": "original response string"
    }
    """

    client = OpenAI(api_key=ApiKeys.openai_key)

    prompt = f"""
    You are a travel assistant. I am planning to visit {destination_city}, {destination_state} from {start_date} to {end_date}.
    I am interested in {activity}. Provide a JSON with the following strict structure:

    {{
        "what_attraction_to_visit_regarding_activity": ["Name 1", "Name 2", "Name 3"],
        "what_is_best_to_do_on_chosen_dates": {{
            "YYYY-MM-DD": "description",
            "YYYY-MM-DD": "description"
        }}
    }}

    - "what_attraction_to_visit_regarding_activity" must be a flat list of strings.
    - "what_is_best_to_do_on_chosen_dates" must be a dictionary with date strings as keys and plain text as values.
    - Return valid JSON ONLY. Do not include explanations, markdown, or notes.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)

        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("Top-level response is not a dictionary.")

        if "what_attraction_to_visit_regarding_activity" not in data or \
                "what_is_best_to_do_on_chosen_dates" not in data:
            raise ValueError("Missing required keys.")

        if not isinstance(data["what_attraction_to_visit_regarding_activity"], list) or \
                not all(isinstance(item, str) for item in data["what_attraction_to_visit_regarding_activity"]):
            raise ValueError("'what_attraction_to_visit_regarding_activity' must be a list of strings.")

        if not isinstance(data["what_is_best_to_do_on_chosen_dates"], dict) or \
                not all(isinstance(k, str) and isinstance(v, str) for k, v in
                        data["what_is_best_to_do_on_chosen_dates"].items()):
            raise ValueError("'what_is_best_to_do_on_chosen_dates' must be a dict with string keys and values.")

        return data

    except (json.JSONDecodeError, ValueError) as e:
        return {"error": str(e), "raw_output": content}
