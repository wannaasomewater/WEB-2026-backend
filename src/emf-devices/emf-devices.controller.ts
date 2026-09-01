import { Controller, Get, Param, Query, Render } from '@nestjs/common';
import { EMFDevicesService } from './emf-devices.service';

@Controller('devices')
export class EMFDevicesController {
  constructor(private readonly emfDevicesService: EMFDevicesService) {}

  @Get()
  @Render('devices-list')
  getDevices(@Query('maxPower') maxPower?: string) {
    return {
      devices: this.emfDevicesService.getAllDevices(maxPower),
      maxPower: maxPower || '',
      pageTitle: 'Список бытовых приборов'
    };
  }

  @Get('draft')
  @Render('device-draft')
  getDraftDevice() {
    return {
      device: this.emfDevicesService.getDraftDevice(),
      pageTitle: 'Добавление прибора'
    };
  }

  @Get(':id')
  @Render('device-feed')
  getDeviceById(@Param('id') id: string, @Query('next') next?: string) {
    return {
      device: this.emfDevicesService.getDeviceById(Number(id), next === 'true'),
      pageTitle: 'Информация о приборе'
    };
  }
}
