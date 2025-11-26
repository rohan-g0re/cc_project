import UploadCard from "../components/UploadCard";
import SearchCard from "../components/SearchCard";

export default function HomePage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
      <UploadCard />
      <SearchCard />
    </div>
  );
}


