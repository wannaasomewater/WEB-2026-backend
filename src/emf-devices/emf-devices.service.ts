import { Injectable } from '@nestjs/common';
import { EMFDevice } from './emf-device.model';

@Injectable()
export class EMFDevicesService {
  private devices: EMFDevice[] = [
    {
      id: 1,
      deviceName: 'Холодильник Samsung RL432',
      deviceType: 'Холодильник',
      powerConsumption: 250,
      frequencyRange: '50 Гц',
      emfLevel: 2.5,
      description: 'Современный холодильник с низким уровнем ЭМП',
      status: 'published',
      imageUrl: 'http://localhost:9000/emf-devices-images/refrigerator.jpg',
      videoUrl: 'http://localhost:9000/emf-devices-images/refrigerator.mp4',
      safetyDistance: 0.5,
      createdAt: new Date('2026-01-15'),
      createdBy: 'admin'
    },
    {
      id: 2,
      deviceName: 'Микроволновая печь LG MS2042',
      deviceType: 'СВЧ-печь',
      powerConsumption: 800,
      frequencyRange: '2450 МГц',
      emfLevel: 25.0,
      description: 'Микроволновая печь с защитным экраном',
      status: 'draft',
      imageUrl: 'http://localhost:9000/emf-devices-images/microwave.jpg',
      videoUrl: 'http://localhost:9000/emf-devices-images/microwave.mp4',
      safetyDistance: 1.0,
      createdAt: new Date('2026-01-20'),
      createdBy: 'user1'
    },
    {
      id: 3,
      deviceName: 'Wi-Fi роутер TP-Link Archer',
      deviceType: 'Сетевое оборудование',
      powerConsumption: 12,
      frequencyRange: '2.4-5 ГГц',
      emfLevel: 10.0,
      description: 'Двухдиапазонный Wi-Fi роутер',
      status: 'deleted',
      imageUrl: 'http://localhost:9000/emf-devices-images/router.jpg',
      videoUrl: 'http://localhost:9000/emf-devices-images/router.mp4',
      safetyDistance: 2.0,
      createdAt: new Date('2026-01-10'),
      createdBy: 'admin'
    }
  ];

  private likes: Array<{ userId: number; deviceId: number }> = [
    { userId: 1, deviceId: 1 },
    { userId: 1, deviceId: 3 },
    { userId: 2, deviceId: 1 },
    { userId: 2, deviceId: 2 },
    { userId: 3, deviceId: 1 }
  ];

  getAllDevices(maxPower?: string): any[] {
    let devices = this.devices.filter(d => d.status !== 'deleted');
    
    if (maxPower) {
      const powerLimit = Number(maxPower);
      if (!isNaN(powerLimit)) {
        devices = devices.filter(d => d.powerConsumption <= powerLimit);
      }
    }
    
    return devices.map(device => ({
      ...device,
      likesCount: this.getLikesCount(device.id)
    }));
  }

  getDraftDevice(): any {
    const draftDevice = this.devices.find(d => d.status === 'draft');
    if (draftDevice) {
      return {
        ...draftDevice,
        likesCount: this.getLikesCount(draftDevice.id)
      };
    }
    return null;
  }

  getDeviceById(id: number, next: boolean = false): any {
    let device = this.devices.find(d => d.id === id && d.status !== 'deleted');
    
    if (next && device) {
      const publishedDevices = this.devices.filter(d => d.status === 'published');
      const currentIndex = publishedDevices.findIndex(d => d.id === device.id);
      const nextIndex = (currentIndex + 1) % publishedDevices.length;
      device = publishedDevices[nextIndex];
    }
    
    if (device) {
      return {
        ...device,
        likesCount: this.getLikesCount(device.id)
      };
    }
    return null;
  }

  private getLikesCount(deviceId: number): number {
    return this.likes.filter(l => l.deviceId === deviceId).length;
  }
}
