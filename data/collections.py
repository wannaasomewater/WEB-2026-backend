emf_devices_db = [
    {
        "id": 1,
        "device_name": "Холодильник Samsung RL432",
        "device_type": "Холодильник",
        "power_consumption": 250,
        "emf_level": 2.5,
        "frequency_range": "50 Гц",
        "safety_distance": 0.5,
        "description": "Современный холодильник с инверторным компрессором и низким уровнем электромагнитного излучения",
        "status": "published",
        "image_url": "http://localhost:9000/emf-devices/refrigerator.jpg",
        "video_url": "http://localhost:9000/emf-devices/refrigerator.mp4",
        "created_at": "2026-01-15",
        "created_by": "admin"
    },
    {
        "id": 2,
        "device_name": "Микроволновая печь LG MS2042",
        "device_type": "СВЧ-печь",
        "power_consumption": 800,
        "emf_level": 25.0,
        "frequency_range": "2450 МГц",
        "safety_distance": 1.0,
        "description": "Микроволновая печь с защитным экраном и системой равномерного распределения волн",
        "status": "draft",
        "image_url": "http://localhost:9000/emf-devices/microwave.jpg",
        "video_url": "http://localhost:9000/emf-devices/microwave.mp4",
        "created_at": "2026-01-20",
        "created_by": "user1"
    },
    {
        "id": 3,
        "device_name": "Wi-Fi роутер TP-Link Archer AX73",
        "device_type": "Сетевое оборудование",
        "power_consumption": 12,
        "emf_level": 10.0,
        "frequency_range": "2.4-5 ГГц",
        "safety_distance": 2.0,
        "description": "Двухдиапазонный Wi-Fi роутер с поддержкой Wi-Fi 6. Технология Beamforming направляет сигнал к устройствам, снижая уровень электромагнитного излучения",
        "status": "deleted",
        "image_url": "http://localhost:9000/emf-devices/router.jpg",
        "video_url": "http://localhost:9000/emf-devices/router.mp4",
        "created_at": "2026-01-10",
        "created_by": "admin"
    }
]

device_likes = [
    {"user_id": 1, "device_id": 1},
    {"user_id": 1, "device_id": 3},
    {"user_id": 2, "device_id": 1},
    {"user_id": 2, "device_id": 2},
    {"user_id": 3, "device_id": 1}
]
