"use client";

import React, { useState, useRef, useMemo } from "react";
import { Search, Filter, School as SchoolIcon, ArrowUpDown } from "lucide-react";
import { School, Language } from "@/types";
import { translations } from "@/lib/i18n";

interface VirtualSchoolTableProps {
  schools: School[];
  lang: Language;
  highContrast: boolean;
  isLoading: boolean;
}

const ROW_HEIGHT = 48; // Constant row height in px for mathematical virtualization
const VIEWPORT_HEIGHT = 480; // Viewport height in px
const OVERSCAN = 5; // Extra rows rendered above/below to prevent blank flickering on fast scroll

export default function VirtualSchoolTable({
  schools,
  lang,
  highContrast,
  isLoading,
}: VirtualSchoolTableProps) {
  const t = translations[lang];
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [sortAsc, setSortAsc] = useState(false);

  // Extract unique districts for filter dropdown
  const uniqueDistricts = useMemo(() => {
    const set = new Set<string>();
    schools.forEach((s) => set.add(s.district));
    return Array.from(set).sort();
  }, [schools]);

  // Filter & Sort Pipeline
  const filteredSchools = useMemo(() => {
    return schools
      .filter((s) => {
        const matchesSearch =
          s.school_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (s.udise_code && s.udise_code.includes(searchTerm));
        const matchesDistrict = selectedDistrict ? s.district === selectedDistrict : true;
        return matchesSearch && matchesDistrict;
      })
      .sort((a, b) => (sortAsc ? a.total_students - b.total_students : b.total_students - a.total_students));
  }, [schools, searchTerm, selectedDistrict, sortAsc]);

  // Virtual Window Calculations
  const totalCount = filteredSchools.length;
  const totalHeight = totalCount * ROW_HEIGHT;

  const startIndex = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - OVERSCAN);
  const visibleCount = Math.ceil(VIEWPORT_HEIGHT / ROW_HEIGHT) + 2 * OVERSCAN;
  const endIndex = Math.min(totalCount, startIndex + visibleCount);

  const visibleRows = useMemo(() => {
    return filteredSchools.slice(startIndex, endIndex);
  }, [filteredSchools, startIndex, endIndex]);

  const paddingTop = startIndex * ROW_HEIGHT;

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return (
    <div
      className={`rounded-xl border shadow-sm p-4 sm:p-6 transition-colors ${
        highContrast
          ? "bg-black border-yellow-400 text-yellow-400"
          : "bg-white border-gray-200 text-gray-900"
      }`}
    >
      {/* Header & Metric Counter */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <SchoolIcon className="w-5 h-5 text-indigo-600" aria-hidden="true" />
            <h2 className="text-lg font-bold">{t.tableHeading}</h2>
          </div>
          <p
            className={`text-xs mt-1 ${
              highContrast ? "text-yellow-200" : "text-gray-500"
            }`}
          >
            {t.tableSubheading}
          </p>
        </div>

        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold ${
            highContrast
              ? "bg-yellow-400 text-black border border-black font-bold"
              : "bg-indigo-50 text-indigo-700 border border-indigo-200"
          }`}
          role="status"
          aria-live="polite"
        >
          <span>{t.totalLoaded}:</span>
          <span className="text-sm font-mono">{filteredSchools.length.toLocaleString()}</span>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search
            className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            aria-hidden="true"
          />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t.searchPlaceholder}
            aria-label={t.searchPlaceholder}
            className={`w-full pl-9 pr-4 py-2 text-sm rounded-lg border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 placeholder-yellow-600 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400 focus-visible:ring-indigo-600"
            }`}
          />
        </div>

        {/* District Filter Dropdown */}
        <div className="relative w-full sm:w-56">
          <Filter
            className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            aria-hidden="true"
          />
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            aria-label="Filter schools by Gujarat District"
            className={`w-full pl-9 pr-8 py-2 text-sm rounded-lg border appearance-none transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
              highContrast
                ? "bg-black border-yellow-400 text-yellow-400 focus-visible:ring-yellow-400"
                : "bg-gray-50 border-gray-300 text-gray-900 focus-visible:ring-indigo-600"
            }`}
          >
            <option value="">{t.filterDistrict}</option>
            {uniqueDistricts.map((dist) => (
              <option key={dist} value={dist}>
                {dist}
              </option>
            ))}
          </select>
        </div>

        {/* Sort Order Toggle */}
        <button
          type="button"
          onClick={() => setSortAsc(!sortAsc)}
          aria-label={`Sort by enrolled students ${sortAsc ? "descending" : "ascending"}`}
          className={`inline-flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
            highContrast
              ? "border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black focus-visible:ring-yellow-400"
              : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-indigo-600"
          }`}
        >
          <ArrowUpDown className="w-3.5 h-3.5" aria-hidden="true" />
          <span>{sortAsc ? "Lowest First" : "Highest First"}</span>
        </button>
      </div>

      {/* ARIA-Compliant Virtualized Table Container (WCAG 2.1 AA) */}
      <div
        className={`rounded-lg border overflow-hidden ${
          highContrast ? "border-yellow-400" : "border-gray-200"
        }`}
      >
        {/* Fixed Header Row */}
        <div
          role="row"
          className={`grid grid-cols-12 text-xs font-bold uppercase tracking-wider py-3 px-4 border-b ${
            highContrast
              ? "bg-yellow-400 text-black border-yellow-400"
              : "bg-gray-100 text-gray-700 border-gray-200"
          }`}
        >
          <div role="columnheader" className="col-span-1">
            {t.columnId}
          </div>
          <div role="columnheader" className="col-span-5 sm:col-span-5">
            {t.columnSchoolName}
          </div>
          <div role="columnheader" className="col-span-3 sm:col-span-3">
            {t.columnDistrict}
          </div>
          <div role="columnheader" className="col-span-3 sm:col-span-2 text-right">
            {t.columnTotalStudents}
          </div>
          <div role="columnheader" className="hidden sm:block sm:col-span-1 text-center">
            {t.columnActions}
          </div>
        </div>

        {/* Scrollable Virtual Viewport */}
        <div
          ref={containerRef}
          onScroll={handleScroll}
          tabIndex={0}
          role="region"
          aria-label="Scrollable list of Gujarat schools"
          style={{ height: `${VIEWPORT_HEIGHT}px` }}
          className="overflow-y-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600"
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-2">
                <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs">Loading State Registry...</span>
              </div>
            </div>
          ) : filteredSchools.length === 0 ? (
            <div className="flex items-center justify-center h-full text-xs text-gray-500">
              No matching schools found for selected criteria.
            </div>
          ) : (
            <div
              role="rowgroup"
              style={{
                height: `${totalHeight}px`,
                position: "relative",
              }}
            >
              <div
                style={{
                  transform: `translateY(${paddingTop}px)`,
                  position: "absolute",
                  left: 0,
                  right: 0,
                  top: 0,
                }}
              >
                {visibleRows.map((school, index) => {
                  const absoluteIndex = startIndex + index;
                  return (
                    <div
                      key={school.id}
                      role="row"
                      tabIndex={0}
                      style={{ height: `${ROW_HEIGHT}px` }}
                      className={`grid grid-cols-12 items-center text-xs px-4 border-b transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                        highContrast
                          ? absoluteIndex % 2 === 0
                            ? "bg-black text-yellow-400 border-yellow-900"
                            : "bg-zinc-950 text-yellow-300 border-yellow-900"
                          : absoluteIndex % 2 === 0
                          ? "bg-white hover:bg-indigo-50/40 border-gray-100"
                          : "bg-gray-50/60 hover:bg-indigo-50/40 border-gray-100"
                      }`}
                    >
                      <div role="cell" className="col-span-1 font-mono text-gray-500">
                        {school.id}
                      </div>
                      <div role="cell" className="col-span-5 sm:col-span-5 font-medium truncate pr-2">
                        {school.school_name}
                      </div>
                      <div role="cell" className="col-span-3 sm:col-span-3 truncate">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium ${
                            highContrast
                              ? "border border-yellow-400 text-yellow-400"
                              : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {school.district}
                        </span>
                      </div>
                      <div role="cell" className="col-span-3 sm:col-span-2 text-right font-mono font-semibold">
                        {school.total_students.toLocaleString()}
                      </div>
                      <div role="cell" className="hidden sm:block sm:col-span-1 text-center">
                        <span
                          className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            highContrast
                              ? "bg-yellow-400 text-black"
                              : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          }`}
                        >
                          {t.statusRecognized}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
