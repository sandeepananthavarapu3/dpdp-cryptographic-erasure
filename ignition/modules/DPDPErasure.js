import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const DPDPErasureModule = buildModule("DPDPErasureModule", (m) => {
  const erasure = m.contract("DPDPErasure");

  return { erasure };
});

export default DPDPErasureModule;
