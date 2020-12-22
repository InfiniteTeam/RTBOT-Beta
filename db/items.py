from utils.datamgr import Item
from .itemtags import Tag

ETC = (
    Item('galaxy_zflip', '갤럭시 Z플립', '모 회사의 폴더블 스마트폰이다.', 100, '📱', tags=[Tag.Phone], selling=8000),

    Item('crucian_carp', '붕어', '그냥 흔한 붕어다.', 100, '🐟', tags=[Tag.Fish], meta={'catchable': True, 'percentage': 8}, selling=4000),
    Item('carp', '잉어', '뭐라할 거 없이 그냥 잉어.', 100, '🐟', tags=[Tag.Fish], meta={'catchable': True, 'percentage': 6.5}, selling=6000),
    Item('salmon', '연어', '몸의 색이 붉은 연어다. 개발자 알파가 생선회 중 가장 좋아하는 거라고 한다.', 100, '🐟', tags=[Tag.Fish], meta={'catchable': True, 'percentage': 2.2}, selling=8000),
    Item('tuna', '참치', '엄청 크다.', 100, '🐟', tags=[Tag.Fish], meta={'catchable': True, 'percentage': 1}, selling=12000),

    Item('common_fishing_rod', '평범한 낚싯대', '공짜로 주는 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 1}, selling=0),
    Item('wooden_fishing_rod', '나무 낚싯대', '나뭇가지로 만든 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 1.2}, selling=800),
    Item('plastic_fishing_rod', '플라스틱 낚싯대', '플라스틱으로 만든 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 1.8}, selling=1800),
    Item('iron_fishing_rod', '쇠 낚싯대', '철로 만든 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 2.2}, selling=20000),
    Item('gold_fishing_rod', '황금 낚싯대', '황금으로 만든 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 2.8}, selling=100000),
    Item('ceramic_fishing_rod', '세라믹 낚싯대', '세라믹으로 만든 낚싯대이다.', 100, '🎣', tags=[Tag.FishingRod], meta={'luck': 3.4}, selling=1800000),
)