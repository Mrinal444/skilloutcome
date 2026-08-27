export const stats = [
  { label: "Total trainees", value: "10,000", delta: "+12.4% vs last period" },
  { label: "Placed", value: "7,200", delta: "+15.2% vs last period" },
  { label: "Retention (6 mo)", value: "82%", delta: "+6.1% vs last period" },
  { label: "Avg salary", value: "\u20B94.8 LPA", delta: "+8.6% vs last period" },
];

export const placementTrend = [
  { m: "Jan", rate: 58 },
  { m: "Feb", rate: 61 },
  { m: "Mar", rate: 65 },
  { m: "Apr", rate: 68 },
  { m: "May", rate: 70 },
  { m: "Jun", rate: 72 },
];

export const skillGaps = [
  { skill: "Python", demand: 82, proficiency: 61 },
  { skill: "SQL", demand: 68, proficiency: 54 },
  { skill: "Data analysis", demand: 61, proficiency: 47 },
  { skill: "AWS", demand: 55, proficiency: 33 },
  { skill: "Excel", demand: 40, proficiency: 58 },
];

export const providers = [
  { name: "TechSkill Academy", rate: 81 },
  { name: "Digital Bridge", rate: 74 },
  { name: "NextGen IT", rate: 76 },
  { name: "Rural Skill Mission", rate: 69 },
  { name: "CraftWorks", rate: 63 },
];

export const districts = [
  { name: "Pune", rate: 78 },
  { name: "Nagpur", rate: 71 },
  { name: "Nashik", rate: 66 },
  { name: "Aurangabad", rate: 60 },
  { name: "Kolhapur", rate: 58 },
];
export const traineeProfiles = {
  "Aarav Sharma": {
    name: "Aarav Sharma",
    traineeId: "MH-PUN-2025-05600",

    course: "CNC Operator",
    district: "Pune",

    status: "EMPLOYED",
    employmentVerified: true,

    journey: {
      training: true,
      certification: true,
      placement: true,
      employment: true,
      retention3M: true,
      retention6M: true,
      retention12M: false,
    },

    employment: {
      employer: "Tata Manufacturing Solutions Pvt. Ltd.",
      role: "CNC Operator",
      joiningDate: "10 March 2025",
      currentSalary: "₹25,500/month",
    },

    wageProgression: [
      {
        label: "Starting",
        salary: "₹18,500",
      },
      {
        label: "3 Months",
        salary: "₹21,000",
      },
      {
        label: "6 Months",
        salary: "₹23,000",
      },
      {
        label: "Current",
        salary: "₹25,500",
      },
    ],

    growth: "+37.8%",

    followups: [
      {
        date: "10 Mar",
        text: "Placement confirmed",
        done: true,
      },
      {
        date: "10 Jun",
        text: "3M follow-up",
        done: true,
      },
      {
        date: "10 Sep",
        text: "6M follow-up",
        done: true,
      },
      {
        date: "10 Dec",
        text: "9M follow-up pending",
        done: false,
      },
    ],
  },

  "Priya Das": {
    name: "Priya Das",
    traineeId: "MH-NGP-2025-05601",

    course: "Data Analytics",
    district: "Nagpur",

    status: "EMPLOYED",
    employmentVerified: true,

    journey: {
      training: true,
      certification: true,
      placement: true,
      employment: true,
      retention3M: true,
      retention6M: true,
      retention12M: false,
    },

    employment: {
      employer: "Infoserve Analytics Pvt. Ltd.",
      role: "Junior Data Analyst",
      joiningDate: "18 March 2025",
      currentSalary: "₹29,000/month",
    },

    wageProgression: [
      {
        label: "Starting",
        salary: "₹23,000",
      },
      {
        label: "3 Months",
        salary: "₹25,000",
      },
      {
        label: "6 Months",
        salary: "₹27,000",
      },
      {
        label: "Current",
        salary: "₹29,000",
      },
    ],

    growth: "+26.1%",

    followups: [
      {
        date: "18 Mar",
        text: "Placement confirmed",
        done: true,
      },
      {
        date: "18 Jun",
        text: "3M follow-up",
        done: true,
      },
      {
        date: "18 Sep",
        text: "6M follow-up",
        done: true,
      },
      {
        date: "18 Dec",
        text: "9M follow-up pending",
        done: false,
      },
    ],
  },

  "Rahul Patil": {
    name: "Rahul Patil",
    traineeId: "MH-PUN-2025-08421",

    course: "CNC Operator",
    district: "Pune",

    status: "EMPLOYED",
    employmentVerified: true,

    journey: {
      training: true,
      certification: true,
      placement: true,
      employment: true,
      retention3M: true,
      retention6M: true,
      retention12M: false,
    },

    employment: {
      employer: "ABC Manufacturing Pvt. Ltd.",
      role: "CNC Operator",
      joiningDate: "14 March 2025",
      currentSalary: "₹24,500/month",
    },

    wageProgression: [
      {
        label: "Starting",
        salary: "₹18,000",
      },
      {
        label: "3 Months",
        salary: "₹20,000",
      },
      {
        label: "6 Months",
        salary: "₹22,000",
      },
      {
        label: "Current",
        salary: "₹24,500",
      },
    ],

    growth: "+36.1%",

    followups: [
      {
        date: "14 Mar",
        text: "Placement confirmed",
        done: true,
      },
      {
        date: "14 Jun",
        text: "3M follow-up",
        done: true,
      },
      {
        date: "14 Sep",
        text: "6M follow-up",
        done: true,
      },
      {
        date: "14 Dec",
        text: "9M follow-up pending",
        done: false,
      },
    ],
  },
};