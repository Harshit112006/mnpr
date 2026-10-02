import { ScanSearch } from "lucide-react";

function BrandLogo() {
  return (
    <div className="brand-logo">
      <div className="brand-logo-icon">
        <ScanSearch size={26} strokeWidth={2.2} />
      </div>

      <div>
        <h1>BreedVision AI</h1>
        <p>Intelligent Bovine Identification</p>
      </div>
    </div>
  );
}

export default BrandLogo;