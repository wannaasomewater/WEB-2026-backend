import { Module } from '@nestjs/common';
import { EMFDevicesController } from './emf-devices/emf-devices.controller';
import { EMFDevicesService } from './emf-devices/emf-devices.service';

@Module({
  imports: [],
  controllers: [EMFDevicesController],
  providers: [EMFDevicesService],
})
export class AppModule {}
