import React from "react"
import { createRoot, type Root } from "react-dom/client"
import { AreaChart } from "./components/dither-kit/area-chart"
import { Area } from "./components/dither-kit/area"
import { BarChart } from "./components/dither-kit/bar-chart"
import { Bar } from "./components/dither-kit/bar"
import type { ChartConfig } from "./components/dither-kit/chart-context"
import { Grid } from "./components/dither-kit/grid"
import { Legend } from "./components/dither-kit/legend"
import { PieChart } from "./components/dither-kit/pie-chart"
import { Pie } from "./components/dither-kit/pie"
import { Tooltip } from "./components/dither-kit/tooltip"
import { XAxis } from "./components/dither-kit/x-axis"
import { YAxis } from "./components/dither-kit/y-axis"

type NamedValue={name:string,value:number}
type Coverage={label:string,runs:number}
type Trend={label:string,findings:number,errors:number}
export type DashboardCharts={severity:NamedValue[];steps:NamedValue[];coverage:Coverage[];trend:Trend[]}
const roots=new Map<string,Root>()
const palette=["red","orange","blue","green","purple"] as const

function mount(id:string,node:React.ReactNode){const element=document.getElementById(id);if(!element)return;let root=roots.get(id);if(!root){root=createRoot(element);roots.set(id,root)}root.render(node)}
const axis=(value:number)=>Math.round(value).toLocaleString()
function configFor(data:NamedValue[]):ChartConfig{return Object.fromEntries(data.map((row,index)=>[row.name,{label:row.name,color:palette[index%palette.length]}]))}
function Empty(){return <div className="flex h-full items-center justify-center border border-dashed text-xs uppercase tracking-wider opacity-60">No run data yet</div>}
function Severity({data}:{data:NamedValue[]}){if(!data.length)return <Empty/>;return <PieChart data={data} config={configFor(data)} dataKey="value" nameKey="name" innerRadius={0.6} className="webops-dither-chart" bloom="low"><Pie variant="dotted"/><Legend/><Tooltip/></PieChart>}
function Steps({data}:{data:NamedValue[]}){if(!data.length)return <Empty/>;return <PieChart data={data} config={configFor(data)} dataKey="value" nameKey="name" innerRadius={0.6} className="webops-dither-chart" bloom="low"><Pie variant="gradient"/><Legend/><Tooltip/></PieChart>}
function TrendChart({data}:{data:Trend[]}){if(!data.length)return <Empty/>;const config:ChartConfig={findings:{label:"All findings",color:"blue"},errors:{label:"Errors",color:"red"}};return <AreaChart data={data} config={config} className="webops-dither-chart" bloom="low"><Grid/><Area dataKey="findings" variant="gradient"/><Area dataKey="errors" variant="dotted"/><XAxis dataKey="label" maxTicks={8}/><YAxis tickFormatter={axis}/><Legend/><Tooltip labelKey="label"/></AreaChart>}
function CoverageChart({data}:{data:Coverage[]}){if(!data.length)return <Empty/>;const config:ChartConfig={runs:{label:"Runs",color:"purple"}};return <BarChart data={data} config={config} className="webops-dither-chart" bloom="low"><Grid/><Bar dataKey="runs" variant="dotted"/><XAxis dataKey="label" maxTicks={10}/><YAxis tickFormatter={axis}/><Tooltip labelKey="label"/></BarChart>}
export function renderCharts(data:DashboardCharts){mount("chartSeverity",<Severity data={data.severity}/>);mount("chartSteps",<Steps data={data.steps}/>);mount("chartTrend",<TrendChart data={data.trend}/>);mount("chartCoverage",<CoverageChart data={data.coverage}/>)}
