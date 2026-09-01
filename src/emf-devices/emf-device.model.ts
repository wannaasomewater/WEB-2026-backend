export type DeviceStatus = 'draft' | 'published' | 'deleted';

export interface EMFDevice {
  id: number;
  deviceName: string;
  deviceType: string;
  powerConsumption: number;
  frequencyRange: string;
  emfLevel: number;
  description: string;
  status: DeviceStatus;
  imageUrl: string;
  videoUrl: string;
  safetyDistance: number;
  createdAt: Date;
  createdBy: string;
}
