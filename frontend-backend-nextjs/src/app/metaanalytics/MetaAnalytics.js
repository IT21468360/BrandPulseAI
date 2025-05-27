'use client';
import dynamic from 'next/dynamic';

const MetaAnalytics = dynamic(() => import('./MetaAnalytics'), { ssr: false });

export default function MetadataPage() {
  return <MetaAnalytics />;
}
